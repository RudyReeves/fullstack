''' Handlers for the Google+ signin flow '''

from flask import redirect, request, render_template, make_response
import random, string, requests, httplib2
import views, db

def get_login_state():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32)) #NOQA
    views.login_session['state'] = state

    logged_in = False
    username = ''
    if is_logged_in():
        logged_in = True
        username = views.login_session['username']

    return (state, logged_in, username)

def is_logged_in():
    return ('username' in views.login_session) and (views.login_session['username'] is not None)

@views.app.route('/gconnect', methods=['POST'])
def gconnect():
    if is_logged_in():
        categories = db.get_categories()
        categories = [category.name for category in categories]
        latest_items = db.get_items()
        latest_items = [[item.name, db.get_category_name_by_id(item.category_id)] for item in latest_items] #NOQA
        data = {
            'categories': categories,
            'latest_items': latest_items,
            'logged_in': True,
            'username': views.login_session['username']
        }
        return render_template('index.html', data = data)

    if request.args.get('state') != views.login_session['state']:
        response = make_response(views.json.dumps('Invalid state paremeter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = views.flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except views.FlowExchangeError:
        response = make_response(views.json.dumps('Failed to upgrade the authorization code.'), 401) #NOQA
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid:
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token) #NOQA
    http = httplib2.Http()
    result = views.json.loads(http.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(views.json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user:
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response("Token's user ID doesn't match given user ID.", 401) #NOQA
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app:
    if result['issued_to'] != views.CLIENT_ID:
        response = make_response(views.json.dumps("Token's client ID does not match app's."), 401) #NOQA
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_credentials = views.login_session.get('credentials')
    stored_gplus_id = views.login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id  == stored_gplus_id:
        response = make_response(views.json.dumps("Current user is already connected."), 200) #NOQA
        response.headers['Content-Type'] = 'application/json'

    # Get user info
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params = params)
    data = views.json.loads(answer.text)

    # Store the access token in the session for later use.
    views.login_session['credentials'] = credentials.access_token
    views.login_session['gplus_id'] = gplus_id
    views.login_session['username'] = data['name']

    # Add a new user if this user doesn't already exist
    user_id = db.get_user_id_by_name(data['name'])
    if not user_id:
        user_id = db.create_user(views.login_session)

    views.login_session['user_id'] = user_id

    return redirect('/')

@views.app.route('/gdisconnect', methods=['POST'])
def gdisconnect():
    access_token = views.login_session.get('credentials')
    if access_token is None:
        response = make_response(views.json.dumps('User is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    http = httplib2.Http()
    result = http.request(url, 'GET')[0]

    if result['status'] == '200':
        del views.login_session['credentials']
        del views.login_session['gplus_id']
        del views.login_session['username']
        del views.login_session['user_id']
        return redirect('/')
    else:
        response = make_response('Failed to logout user.', 400)
        response.headers['Content-Type'] = 'application/json'
        return response