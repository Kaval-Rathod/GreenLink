import os
from fastapi import FastAPI, Depends, HTTPException, status, Body, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import requests
import json

import database, models, schemas, crud, auth
from blockchain import blockchain_service

# Create DB tables (safe to call every start)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="GreenLink API", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# AI Service configuration
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai_service:8001")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"ok": True, "message": "GreenLink backend running."}

# --- Register user (public) ---
@app.post("/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = auth.hash_password(user_in.password)
    user = crud.create_user(db, user_in, hashed)
    return user

# --- Login (OAuth2 password flow) ---
@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = auth.create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

# --- Protected helper to get current user ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user_id = int(payload.get("sub"))
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# --- Read users (admin-style) ---
@app.get("/users", response_model=list[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # For demo: require auth to list users. Later add roles.
    return crud.get_users(db, skip=skip, limit=limit)

@app.get("/users/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/users/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # For now allow updating only by the same user (or we could expand roles)
    if current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Not permitted")
    updated = crud.update_user(db, user, user_update)
    return updated

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user.id:
        raise HTTPException(status_code=403, detail="Not permitted")
    crud.delete_user(db, user)
    return None

# --------- Phase 2: Real AI Integration ---------

@app.post("/upload", response_model=schemas.SubmissionOut, status_code=status.HTTP_201_CREATED)
def upload_photo(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Save file to uploads
    safe_filename = file.filename.replace("..", "_")
    dest_path = UPLOAD_DIR / safe_filename
    # If file exists, add numeric suffix
    counter = 1
    base = dest_path.stem
    ext = dest_path.suffix
    while dest_path.exists():
        dest_path = UPLOAD_DIR / f"{base}_{counter}{ext}"
        counter += 1
    with dest_path.open("wb") as f:
        f.write(file.file.read())

    submission = crud.create_submission(
        db,
        user_id=current_user.id,
        photo_path=str(dest_path),
        latitude=latitude,
        longitude=longitude,
    )
    return submission

@app.get("/submissions", response_model=list[schemas.SubmissionOut])
def list_my_submissions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.list_submissions(db, user_id=current_user.id)

@app.get("/submissions/all", response_model=list[schemas.SubmissionOut])
def list_all_submissions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # For now, allow any authenticated user to list all submissions (later add roles)
    return crud.list_submissions(db, user_id=None)

@app.post("/analyze/{submission_id}", response_model=schemas.SubmissionOut)
def analyze_submission(submission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    submission = crud.get_submission(db, submission_id)
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Submission not found")

    try:
        # Call AI service for real analysis
        ai_response = requests.post(
            f"{AI_SERVICE_URL}/analyze-path",
            json={"image_path": submission.photo_path},
            timeout=30
        )
        
        if ai_response.status_code == 200:
            ai_results = ai_response.json()
            greenery_pct = ai_results["greenery_percentage"]
            carbon_value = ai_results["carbon_value"]
        else:
            # Fallback to placeholder if AI service fails
            print(f"AI service error: {ai_response.status_code} - {ai_response.text}")
            greenery_pct = 42.0
            carbon_value = round(greenery_pct * 0.01 * 0.5, 3)
            
    except Exception as e:
        # Fallback to placeholder if AI service is unavailable
        print(f"AI service unavailable: {str(e)}")
        greenery_pct = 42.0
        carbon_value = round(greenery_pct * 0.01 * 0.5, 3)

    updated = crud.update_submission_analysis(db, submission, greenery_pct, carbon_value)
    return updated

@app.get("/credits", response_model=list[schemas.CreditOut])
def list_my_credits(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.list_credits(db, user_id=current_user.id)

@app.get("/ai-status")
def get_ai_status():
    """Get AI service status"""
    try:
        response = requests.get(f"{AI_SERVICE_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"AI service returned {response.status_code}"}
    except Exception as e:
        return {"status": "unavailable", "message": str(e)}

# --------- Phase 3: Blockchain Integration ---------

@app.get("/blockchain/status")
def get_blockchain_status():
    """Get blockchain connection status"""
    return blockchain_service.get_network_info()

@app.post("/blockchain/mint/{submission_id}")
def mint_carbon_credit(submission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Mint carbon credit token for a submission"""
    submission = crud.get_submission(db, submission_id)
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if not submission.greenery_pct or not submission.carbon_value:
        raise HTTPException(status_code=400, detail="Submission must be analyzed first")
    
    # Get user's wallet address (for now, use a placeholder)
    user_wallet = current_user.wallet_address or "0x0000000000000000000000000000000000000000"
    
    # Create image URI (in production, this would be IPFS hash)
    image_uri = f"file://{submission.photo_path}"
    
    # Mint token on blockchain
    tx_hash = blockchain_service.mint_carbon_credit(
        to_address=user_wallet,
        carbon_value=submission.carbon_value,
        greenery_percentage=submission.greenery_pct,
        location=f"{submission.gps_coords.x},{submission.gps_coords.y}" if submission.gps_coords else "0,0",
        image_uri=image_uri
    )
    
    if tx_hash:
        # Create credit record in database
        credit = crud.create_credit(db, user_id=current_user.id, tonnes_co2=submission.carbon_value, token_id=tx_hash)
        return {"success": True, "transaction_hash": tx_hash, "credit_id": credit.id}
    else:
        raise HTTPException(status_code=500, detail="Failed to mint token on blockchain")

@app.get("/blockchain/tokens")
def get_user_tokens(current_user: models.User = Depends(get_current_user)):
    """Get user's carbon credit tokens"""
    user_wallet = current_user.wallet_address or "0x0000000000000000000000000000000000000000"
    tokens = blockchain_service.get_user_tokens(user_wallet)
    return {"tokens": tokens, "count": len(tokens)}

@app.get("/blockchain/marketplace")
def get_marketplace_listings():
    """Get active marketplace listings"""
    listings = blockchain_service.get_marketplace_listings()
    return {"listings": listings, "count": len(listings)}

@app.post("/blockchain/register-submission/{submission_id}")
def register_submission_on_blockchain(submission_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Register submission on blockchain registry"""
    submission = crud.get_submission(db, submission_id)
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if not submission.greenery_pct or not submission.carbon_value:
        raise HTTPException(status_code=400, detail="Submission must be analyzed first")
    
    # Get user's wallet address
    user_wallet = current_user.wallet_address or "0x0000000000000000000000000000000000000000"
    
    # Create image hash (in production, this would be IPFS hash)
    image_hash = f"ipfs://{hash(submission.photo_path)}"
    
    # Register on blockchain
    tx_hash = blockchain_service.register_submission(
        user_address=user_wallet,
        image_hash=image_hash,
        greenery_percentage=submission.greenery_pct,
        carbon_value=submission.carbon_value,
        location=f"{submission.gps_coords.x},{submission.gps_coords.y}" if submission.gps_coords else "0,0"
    )
    
    if tx_hash:
        return {"success": True, "transaction_hash": tx_hash}
    else:
        raise HTTPException(status_code=500, detail="Failed to register submission on blockchain")
