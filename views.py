# importing required libraries
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import OIDCConfiguration, Credentials, APICredentials
import requests
import json

# Views for handling OIDC, Pactflow and SwaggerHub integration

def social_media_login(request, platform):
    """
    View to handle login credentials for the social media site
    Retrieves the credentials or API keys stored in the database and sends them to the requested platform for login
    """
    try:
        # Check if there are API keys stored for the platform
        api_keys = APICredentials.objects.filter(platform=platform)
        if not api_keys.exists():
            # If no API keys found, check for username and password
            login_details = Credentials.objects.filter(platform=platform)
            if not login_details.exists():
                return HttpResponse("No login credentials found for the requested platform.")
    except Exception as e:
        return HttpResponse(f"Error while fetching credentials: {e}")

def oidc_auth(request):
    """ 
    View to handle initial OIDC authentication request.  
    """
    if not (config := OIDCConfiguration.objects.first()):
        return HttpResponse("OIDC Configuration not found in database.")
    client_id = config.client_id
    redirect_uri = config.redirect_uris.split(',')[0].strip()

    auth_url = "https://api.bitbucket.org/2.0/workspaces/smodal/pipelines-config/identity/oidc"
        # Constructing and redirecting to authentication URL.
    return redirect(
        f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )

def oidc_callback(request):
    """
    View to handle auth server's callback
    """
    if not (config := OIDCConfiguration.objects.first()):
        return HttpResponse("OIDC Configuration not found in database.")
    token_url = "https://api.bitbucket.org/2.0/workspaces/smodal/pipelines-config/identity/oidc/token"
    client_id = config.client_id
    redirect_uri = config.redirect_uris.split(',')[0].strip()
    client_secret = config.client_secret

    # Getting the authorization code from request parameters
    code = request.GET.get('code')

    # Constructing headers and body for token request.
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    body = {'grant_type': 'authorization_code', 'code': code, 'client_id': client_id, 'client_secret': client_secret, 'redirect_uri': redirect_uri }

    # Making POST request to get tokens.
    r = requests.post(token_url, headers=headers, data=body)

    if r.status_code == 200:
        # If request is successful, redirect to home page after storing tokens.
        access_token = r.json().get('access_token')

            # Making a request to Pactflow.
        pactflow_headers = {'Authorization': f'Bearer {access_token}'}
        r_pactflow = requests.get('https://modaltokai-smodal.pactflow.io', headers=pactflow_headers)
        if r_pactflow.status_code == 200:
            # Save pactflow response details
            response_headers = json.dumps(dict(r_pactflow.headers))
            response_body = json.dumps(r_pactflow.json())

            config.pactflow_response_headers = response_headers
            config.pactflow_response_body = response_body
            config.save()
        else:
            return HttpResponse("Error while fetching data from Pactflow. Please try again")

        # You may store the tokens in database for future use.
        # After storing the tokens, redirect as per your application's flow.
        return redirect('/home/')
    else:
        return HttpResponse("Error while fetching tokens. Please try again.")