from fastapi import (
    APIRouter,
    HTTPException
)
from fastapi.responses import (
    JSONResponse,
    HTMLResponse
)
from .settings import db

import re
import os


router = APIRouter()

# ============= Creating path operations ==============
@router.get("/")
def get_readme():
    return HTMLResponse(
        """
            <!DOCTYPE html>
            <html>            
                 <head>
                    <title>L'Aquarium</title>
                    <link rel="icon" type="image/png" sizes="32x32" href="">
                    <link rel="icon" type="image/png" sizes="16x16" href="">
                    <link rel="manifest" href="">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                    <h4>AQU-API: FastAPI Python 3.9</h4>
                    
                    <p>Server: nginx/unit:1.22.0</p>
                    
                        <p>In your production system, you probably have a frontend created with a modern framework like React, Vue.js, Angular or Laravel.</p> 

                        <p>And to communicate using APIs & WebSocket-APIs with your backend you would probably use your frontend's utilities.</p> 

                        <p>Or you might have a native mobile application that communicates with your WebSocket backend directly, in native code.</p> 

                        <p>Or you might have any other way to communicate with the API endpoint.</p> 
                            
                    <p>RESTful APIs Document: <a href='https://stage.stripe.rankworks.com/docs#'>Swagger</a> <img src="https://htmlcodeeditor.com/images/smiley.png" alt="smiley" /></p>
                
                </body>
            </html>
        """
    )

 