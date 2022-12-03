from fastapi import Depends, HTTPException, Request, status


def get_db(request: Request):
    db = request.app.state.session()
    try:
        yield db
    finally:
        db.close()
