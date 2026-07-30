import jwt
import requests
from django.http import JsonResponse

# Default Keycloak realm URL on Archimede
KEYCLOAK_URL = "http://192.168.8.69:31480/realms/master"

def get_public_key():
    try:
        response = requests.get(KEYCLOAK_URL, timeout=5)
        response.raise_for_status()
        public_key = response.json().get('public_key')
        if not public_key:
            return None
        return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
    except Exception as e:
        print(f"Failed to fetch Keycloak public key: {e}")
        return None

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only protect the O2DMS deployment endpoints
        if not request.path.startswith('/api/o2dms/'):
            return self.get_response(request)

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Unauthorized, Bearer token missing'}, status=401)
        
        token = auth_header.split(' ')[1]
        
        public_key = get_public_key()
        if not public_key:
            return JsonResponse({'error': 'Internal Error, cannot fetch IDP key'}, status=500)

        try:
            # Decode and verify the RS256 signature using the Keycloak public key
            decoded = jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False})
            request.jwt_payload = decoded
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
            
        return self.get_response(request)
