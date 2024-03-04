from ast import Expression
from multiprocessing import context
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from accounts.models import OneTimePassword
from accounts.serializers import PasswordResetRequestSerializer,LogoutUserSerializer, UserRegisterSerializer, LoginSerializer, SetNewPasswordSerializer,BusinessUserSerializer, BusinessDetailsSerializer
from rest_framework import status
from .utils import send_generated_otp_to_sms
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated
from .models import User, BusinessUser, BusinessDetails
# Create your views here.


class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user = request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            send_generated_otp_to_sms(user_data['phone_number'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_id = request.data.get('user')
            user_pass_obj=OneTimePassword.objects.get(user=user_id)
            user=user_pass_obj.user
            if user_pass_obj.otp == passcode:
                if not user.is_verified:
                    user.is_verified=True
                    user.save()
                    return Response({
                        'message':'account email verified successfully'
                    }, status=status.HTTP_200_OK)
                return Response({'message':'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'provided the valid otp'}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        # return Response({'message':'user with that email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    



class PasswordResetConfirm(GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)


class TestingAuthenticatedReq(GenericAPIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):

        data={
            'msg':'its works'
        }
        return Response(data, status=status.HTTP_200_OK)
    
class BusinessUserActivation(GenericAPIView):
    queryset = BusinessUser.objects.all()
    serializer_class = BusinessUserSerializer
    permission_classes=[IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        # If serializer is not valid, try to activate a user
        try:
            ph_number = request.data.get("phone_number")
            user_check = User.objects.get(phone_number=ph_number)
            
            if serializer.is_valid():
                # Check if the phone number already exists in BusinessUser
                phone_number = serializer.validated_data.get('phone_number')
                user = User.objects.get(phone_number=phone_number)
                if BusinessUser.objects.filter(phone_number=phone_number).exists():
                    return Response({'error': 'Phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

                # Create a new BusinessUser
                user.is_business_user = True
                user.save()
                serializer.save()
                return Response({serializer.data, {"Status": "Business Account Activated Successfully"}}, status=status.HTTP_201_CREATED)
            
            elif user_check.is_business_user == True:
                return Response({'message': 'Already Activated'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                 return Response({'message': 'Provide Proper Details'}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({'message': 'User Does Not Exist Bad Gateway check wheather you entered correct verified phone number'}, status=status.HTTP_400_BAD_REQUEST)

class BusinessDetailsListCreateView(ListCreateAPIView):
    queryset = BusinessDetails.objects.all()
    serializer_class = BusinessDetailsSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
                # Check if the phone number already exists in BusinessUser
                business_user = serializer.validated_data.get('business_user')
                business_name = serializer.validated_data.get('business_name')
                phone_number = serializer.validated_data.get('business_phone_number')
                business_email = serializer.validated_data.get('business_email')
                if BusinessDetails.objects.filter(business_user=business_user, business_name__icontains=business_name).exists():
                    return Response({'error': 'You have already registered a business with same details'}, status=status.HTTP_400_BAD_REQUEST)
                
                elif BusinessDetails.objects.filter(business_phone_number=phone_number).exclude(business_user=business_user).exists():
                    return Response({'Caution': 'This is not your phone number/ email id'}, status=status.HTTP_400_BAD_REQUEST)
                
                elif BusinessDetails.objects.filter(business_email=business_email).exclude(business_user=business_user).exists():
                    return Response({'Caution': 'This is not your email id'}, status=status.HTTP_400_BAD_REQUEST)
# Set the business_user field before saving
                else:
                    serializer.save()
                return Response({"Data":serializer.data, "Status": "Business Added Successfully"}, status=status.HTTP_201_CREATED)
        return Response({'Caution': 'Not a Proper Request/ you are not a business user'}, status=status.HTTP_400_BAD_REQUEST)

class BusinessDetailsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = BusinessDetails.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessDetailsSerializer
    lookup_field = 'business_id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Your custom validation logic
        business_user = serializer.validated_data.get('business_user')
        business_name = serializer.validated_data.get('business_name')
        phone_number = serializer.validated_data.get('business_phone_number')
        business_email = serializer.validated_data.get('business_email')

        if BusinessDetails.objects.filter(business_user=business_user, business_name=business_name).exists():
            return Response({'error': 'You have already registered a business with the same details'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif BusinessDetails.objects.filter(business_phone_number=phone_number).exclude(business_user=business_user).exists():
            return Response({'Caution': 'This is not your phone number/ email id'}, status=status.HTTP_400_BAD_REQUEST)
        elif BusinessDetails.objects.filter(business_email=business_email).exclude(business_user=business_user).exists():
            return Response({'Caution': 'This is not your email id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response({"Data":serializer.data, "Status": "Business Added Successfully"}, status=status.HTTP_201_CREATED)
    
class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
 