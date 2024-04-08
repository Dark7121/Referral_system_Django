# Referral_API Detailed Explanations

#HOW TO RUN THIS:
1. Download this file first.
2. Install docker (https://docs.docker.com/engine/install/)
3. Install wsl (wsl --install), After installing it will reboot
4. Now start the ```Docker``` application and Run this command ```docker-compose build```
5. After build is done run ```docker-compose up```
6. Now open another terminal or powershell and type ```docker ps``` and get the ```CONTAINER ID```
7. Now in that same terminal type ```docker exec -it <CONTAINER ID> bash``` and run ```python manage.py makemigrations app``` & ```python manage.py migrate```.
#NOW THE SERVER WILL RUN ON YOUR LOCALHOST

#FOLLOW THIS TO CREATE A USER, LOGIN, GET USER DETAILS & REFERRELS DETAILS
1. ```curl -X POST http://127.0.0.1:8000/register/ -H "Content-Type: application/json" -d "{\"name\": \"John Doe\", \"email\": \"johndow@example.com\", \"password\": \"example@123\"}"``` <--Register User. You Can Also Add Another Field ```referral_id``` For The New Users, And In This Optional Field You Can Enter An Existing User's referral_code.
2. ```curl -X POST http://127.0.0.1:8000/login/ -H "Content-Type: application/json" -d "{\"email\": \"johndow@example.com\", \"password\": \"example@123\"}"``` <--Login User.

#AFTER CREATING AND LOGGING IN YOU WILL GET THE TOKEN WHICH WILL VALID FOR 3 MINTUES, NOW:
1. ```http://127.0.0.1:8000/<your-user_id>/<your-token>/``` <--For User Details.
2. ```http://127.0.0.1:8000/<your-user_id>/<your-token>/``` <--User Details For Those Who Used The Current User's referral_code.

In this Django project, I have built an API that typically responds to some specific calls. But first, let's see the features:


1. User Registration
2. User Login
3. User Details
4. Referred Users by Current User
5. Point System (referrer's side)
6. Token Generation System
7. CustomPagination


Now let's see the ```views.py``` function:


```
def check_referral_code(referral_id):
    user_with_referral = CustomUser.objects.filter(referral_code=referral_id).first()
    if user_with_referral:
        return user_with_referral
    else:
        return Response({"Error": "Invalid Referral ID"}, status=status.HTTP_400_BAD_REQUEST)
```
The above function will give the user whose ```referral_code``` will match with the input. While registering, a new user can use an existing user's ```referral_code```. To make it simple, I used referral_code for ```auto-generating``` and ```referral_id``` where the user can enter another existing user's ```referral_code```.


```
def get_users_referred_by_referral_code(request, user_id):
    try:
        current_user = CustomUser.objects.get(user_id=user_id)
        user_referral_code = current_user.referral_code
        users = CustomUser.objects.filter(referral_id=user_referral_code)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
```
In the above function, it will give us a list of all users who will have the have the current user's ```referral_code```.


```
@api_view(['POST'])
def register_user(request):
    data = request.data.copy()
    data['request_type'] = 'register'
    serializer = UserSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        try:
            user = serializer.save()
            referral_id = data.get('referral_id')
            if referral_id:
                referred_by_user = check_referral_code(referral_id)
                if referred_by_user:
                    referred_by_user.points += 1
                    referred_by_user.save()
            return Response({"user_id": user.user_id, "message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_details(request, user_id, token):
    user = get_object_or_404(CustomUser, user_id=user_id)
    token = user.token
    serializer = UserSerializer(user)
    if serializer:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def referrals(request, user_id, token):
    user = CustomUser.objects.get(user_id=user_id)
    token = user.token
    return get_users_referred_by_referral_code(request, user.user_id)
```


THE ABOVE THREE FUNCTIONS ARE CREATED AND WORKING AS PER THE REQUIREMENTS.


```
@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    token = request.data.get('token')
    user = CustomUser.objects.get(email=email)
    if password==user.password:
        return Response({"token": user.token, "referral_code": user.referral_code, "user_id": user.user_id, "message": "Login successful"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Inavlid Password"}, status=status.HTTP_400_BAD_REQUEST)
```
But for better understanding, I have created an additional function so it will be easy to get the ```referral_code```, ```user_id``` and ```token```.


Now, as mentioned in the requirement that a token is needed for ```Authorization```, I have also added a function that will change the token every 3 minutes as long as the service is up.


For the ```models.py```:


I have changed the user type so the ```username``` problem does not persist.
Alongside, all the ```auto generations``` functions are there as well.


```serializers.py```:
1. First, that password should be seen so it's  ```write_only=True```,
2. ```referral_id``` is an optional field, so it's ```required=False```.
3. For a better understanding, ```get_registration_timestamp``` will convert the UTC time to local time, so it will be easy to track.
4. ```Meta Class``` This class provides metadata for the serializer. It specifies the model ```CustomUser``` that the serializer is based on and the fields that should be included in the serialized output.


```urls.py```:
I have created four urls that will work for ```register```, ```login```, ```user_details``` and ```referrals```.
Example:


```127.0.0.1:8000/user/<str:user_id>/<str:token>/```
```127.0.0.1:8000/user/<str:user_id>/<str:token>/referrals/```


In the ```referral_system/settings.py```:


I have added the ```app``` and ```rest_framework``` as well as configured the ```DATABASES``` and ```REST_FRAMEWORK```.


```docker-compose.yml```:
This file defines services, networks, and volumes for Docker applications.
In this context, it's used to define services like web and db, specify build configurations, set environment variables, expose ports, and define dependencies.
For example, the web service is built from the current directory ```(build: .)```, maps port ```8000```, specifies volumes, and depends on the DB service.


```Dockerfile```:
This file contains instructions for building Docker images.
Typically, it starts with a base image, installs dependencies, copies files into the image, sets environment variables, and specifies the command to run when the container starts.
For example, a ```Dockerfile``` for a Django project might start with a Python base image, install dependencies using ```requirements.txt```, copy project files, set environment variables like ```DJANGO_SETTINGS_MODULE```, and run the Django development server.


```requirements.txt```:
This file lists the Python dependencies required by the project.
When a virtual environment is created using virtualenv or pipenv, running pip install -r requirements.txt installs all dependencies listed in this file.
It's commonly used in Python projects to ensure consistent environments across development, testing, and production.


Starting the Server:
The Docker setup automatically handles starting the server ```runserver``` along with the database.
This is achieved through the configurations in ```docker-compose.yml``` and the command specified in the Dockerfile.
The Docker Compose file defines the services and their interactions, ensuring that necessary services like the database are started before the web service.


----------------------------------------------------------------XXX-------------------------------------------------------------
