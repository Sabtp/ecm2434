from django.test import TestCase, Client
from database.models import User, UserFriend, PendingFriendInvite, CustomAccountManager

from rest_framework.test import APIClient, APITestCase, force_authenticate
from rest_framework_simplejwt.views import *

# Create test cases for testing friends functionality here
class TestFriends(TestCase):

    def setUp(self):
        # Set up test case that runs before every test
        User.objects.create_user(username="TestUser", email="test@gmail.com", password="test")

    def testAllFriendsEndpoint(self):
        # Test that the AllFriends endpoint returns a list of all the friends of the user

        user = User.objects.get(username='TestUser')

        # create 3 users but only add 2 of them as friends
        User.objects.create(username="TestFriend1",
            email="TestFriend1@gmail.com",
            name="TestName")
        User.objects.create(username="TestFriend2",
            email="TestFriend2@gmail.com",
            name="TestName")
        User.objects.create(username="TestFriend3",
            email="TestFriend3@gmail.com",
            name="TestName")
        
        UserFriend.objects.create(user=user, friend=User.objects.get(username="TestFriend1"))
        UserFriend.objects.create(user=user, friend=User.objects.get(username="TestFriend2"))

        c = APIClient()
        c.force_authenticate(user=user)
        
        # test post request to get all of the user's friends
        data = {}
        response = c.post('/friends/allFriends', data=data)
        
        self.assertTrue(len(response.json().get("data")) == 2)
        self.assertTrue({"username" : "TestFriend1"} in response.json().get("data"))

    def testAllPendingInvitesEndpoint(self):
        # Test that the allPending endpoint retuns a dictionary of all the 
        # pending invites the user has yet to accept

        user = User.objects.get(username='TestUser')

        # create 3 users but only have 2 of them request friendship
        User.objects.create(username="TestFriend1",
            email="TestFriend1@gmail.com",
            name="TestName")
        User.objects.create(username="TestFriend2",
            email="TestFriend2@gmail.com",
            name="TestName")
        User.objects.create(username="TestFriend3",
            email="TestFriend3@gmail.com",
            name="TestName")
        
        PendingFriendInvite.objects.create(user=User.objects.get(username="TestFriend1"), potentialFriend=user)
        PendingFriendInvite.objects.create(user=User.objects.get(username="TestFriend3"), potentialFriend=user)

        c = APIClient()
        c.force_authenticate(user=user)
        
        # test post request to get all of the user's pending requests
        data = {}
        response = c.post('/friends/allPending', data=data)

        self.assertTrue(len(response.json().get("data")) == 2)
        self.assertTrue({"username" : "TestFriend3"} in response.json().get("data"))

    def testRequestEndpoint(self):
        # Test that the request endpoint allows the user to request the friendship of another user

        user = User.objects.get(username='TestUser')

        # create another user for the TestUser to request
        User.objects.create(username="TestFriend1",
            email="TestFriend1@gmail.com",
            name="TestName")
        
        c = APIClient()
        c.force_authenticate(user=user)
        
        # send the friend request from the TestUser to the TestFriend1
        data = {"friend username" : "TestFriend1"}
        response = c.post('/friends/request', data=data)

        # check that the invite now shows in the pending invites of TestFriend1
        c = APIClient()
        c.force_authenticate(user=User.objects.get(username="TestFriend1"))
        data = {}
        response = c.post('/friends/allPending', data=data)

        self.assertTrue(len(response.json().get("data")) == 1)
        self.assertTrue(response.json().get("data") == [{'username': 'TestUser'}])

    def testRequestEndpointRepeated(self):
        # Test that the request endpoint can't be used repeatedly on the same user

        user = User.objects.get(username='TestUser')

        # create another user for the TestUser to request
        User.objects.create(username="TestFriend1",
            email="TestFriend1@gmail.com",
            name="TestName")
        
        c = APIClient()
        c.force_authenticate(user=user)
        
        # send the friend request from the TestUser to the TestFriend1 twice
        data = {"friend username" : "TestFriend1"}
        response = c.post('/friends/request', data=data)
        response = c.post('/friends/request', data=data)

        # check that the request only works once
        c = APIClient()
        c.force_authenticate(user=User.objects.get(username="TestFriend1"))
        data = {}
        response = c.post('/friends/allPending', data=data)

        self.assertTrue(len(response.json().get("data")) == 1)
        self.assertTrue(response.json().get("data") == [{'username': 'TestUser'}])

    def testRequestEndpointInvalid(self):
        # Test that the request endpoint doesn't break when passed an invalid username

        user = User.objects.get(username='TestUser')
        
        c = APIClient()
        c.force_authenticate(user=user)
        
        # send the friend request from the TestUser to an invalid username
        data = {"friend username" : "InvalidUser"}
        response = c.post('/friends/request', data=data)

        # check that the friend request was identified as invalid
        self.assertTrue(response.json().get("data") == [])

    def testRequestEndpointForFriends(self):
        # Test that the request endpoint doesn't allow you to request
        # the friendship of a user who is already your friend

        user = User.objects.get(username='TestUser')

        # create another user for the TestUser to be friends with
        friend = User.objects.create(username="TestFriend1",
                    email="TestFriend1@gmail.com",
                    name="TestName")
        
        UserFriend.objects.create(user=user, friend=friend)
        
        c = APIClient()
        c.force_authenticate(user=user)
        
        # send the friend request from the TestUser to an existing friend
        data = {"friend username" : "InvalidUser"}
        response = c.post('/friends/request', data=data)

        # check that the friend request was identified as invalid
        self.assertTrue(response.json().get("data") == [])



