import uuid
import json
from rest_framework.test import APITestCase, APIClient

from djangoldp_community.models import Community
from djangoldp_account.models import LDPUser as User

context = {'@context': {'@vocab': "https://cdn.startinblox.com/owl#"}}

class PermissionsTestCase(APITestCase):
    # Django runs setUp automatically before every test
    def setUp(self):
        # we set up a client, that allows us
        self.client = APIClient()

    # we have custom set up functions for things that we don't want to run before *every* test, e.g. often we want to
    # set up an authenticated user, but sometimes we want to run a test with an anonymous user
    def setUpLoggedInUser(self, is_superuser=False):
        self.user = User(email='test@mactest.co.uk', first_name='Test', last_name='Mactest', username='test',
                         password='glass onion', is_superuser=is_superuser)
        self.user.save()
        # this means that our user is now logged in (as if they had typed username and password)
        self.client.force_authenticate(user=self.user)

    # we write functions like this for convenience - we can reuse between tests
    def _get_random_user(self):
        return User.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test',
                                   last_name='Test',
                                   username=str(uuid.uuid4()))

    def _get_random_community(self):
        return Community.objects.create(name='Test', slug=str(uuid.uuid4()))

    def _add_community_member(self, user, community, is_admin=False):
        community.members.user_set.add(user)
        if is_admin:
            community.admins.user_set.add(user)
    '''
    list communities - public
    list community members - public
    create community - authenticated
    update, delete, control community - community admin only
    create, update, delete, control community member - community admin only
    Admins can't remove admins (or themselves if they're the last admin)
    community projects - apply Project permissions (same for JobOffers and Circles)
    '''
    # only authenticated users can create communities
    def test_post_community_anonymous(self):
        response = self.client.post('/communities/', data=json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_post_community_authenticated(self):
        self.setUpLoggedInUser()
        response = self.client.post('/communities/', data=json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # only community admins can update communities
    def test_update_community_is_admin(self):
        self.setUpLoggedInUser()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=True)
        response = self.client.patch('/communities/{}/'.format(community.slug), data=json.dumps({}),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    def test_update_community_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.patch('/communities/{}/'.format(community.slug), data=json.dumps({}),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_update_community_is_auth_super_user(self):
        self.setUpLoggedInUser(is_superuser=True)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.patch('/communities/{}/'.format(community.slug), data=json.dumps({}),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    # only community admins can delete communities
    def test_delete_community_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=True)
        response = self.client.delete('/communities/{}/'.format(community.slug))
        self.assertEqual(response.status_code, 403)

    def test_delete_community_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.delete('/communities/{}/'.format(community.slug))
        self.assertEqual(response.status_code, 403)

    def test_delete_community_is_auth_super_user(self):
        self.setUpLoggedInUser(is_superuser=True)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.delete('/communities/{}/'.format(community.slug))
        self.assertEqual(response.status_code, 204)

    def test_get_community_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)

        response = self.client.get('/communities/{}/'.format(community.slug))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('add', response.data['permissions'])
        self.assertEqual(len(response.data['permissions']), 1)
        response = self.client.get('/groups/{}/'.format(community.members.id))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('add', response.data['permissions'])
        self.assertEqual(len(response.data['permissions']), 1)

    def test_get_communities_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.get('/communities/')
        self.assertEqual(response.status_code, 200)
        communities = response.data['ldp:contains']
        self.assertEqual(len(communities), 1)

    def test_get_communities_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=True)
        response = self.client.get('/groups/{}/'.format(community.members.id))
        self.assertEqual(response.status_code, 200)

    # only community admins can do any operation on community members
    def test_add_community_member_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=True)
        payload = {'@context': context, 'user_set':[{'@id': another_user.urlid}, {'@id': self.user.urlid}]}
        response = self.client.patch(f'/groups/{community.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(community.members.user_set.count(), 2)

    def test_add_community_member_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        payload = {'@context': context, 'user_set':[{'@id': another_user.urlid}, {'@id': self.user.urlid}]}
        response = self.client.patch(f'/groups/{community.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(community.members.user_set.count(), 1)

    def test_add_community_member_is_admin_no_parent(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=True)
        payload = {'@context': context, 'user_set':[{'@id': another_user.urlid}, {'@id': self.user.urlid}]}
        response = self.client.patch(f'/groups/{community.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(community.members.user_set.count(), 2)

    def test_delete_community_member_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=True)
        self._add_community_member(user=another_user, community=community, is_admin=False)
        payload = {'@context': context, 'user_set':[{'@id': self.user.urlid}]}
        response = self.client.patch(f'/groups/{community.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(community.members.user_set.count(), 1)

    def test_delete_community_member_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        self._add_community_member(user=another_user, community=community, is_admin=False)
        payload = {'@context': context, 'user_set':[{'@id': self.user.urlid}]}
        response = self.client.patch(f'/groups/{community.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(community.members.user_set.count(), 2)

    def test_delete_community_member_is_auth_super_user(self):
        self.setUpLoggedInUser(is_superuser=True)
        another_user = self._get_random_user()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        self._add_community_member(user=another_user, community=community, is_admin=False)
        payload = {'@context': context, 'user_set':[{'@id': self.user.urlid}]}
        response = self.client.patch(f'/groups/{community.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(community.members.user_set.count(), 1)

    # regular users can remove themselves
    def test_delete_self(self):
        self.setUpLoggedInUser(is_superuser=True)
        another_user = self._get_random_user()
        community = self._get_random_community()
        self._add_community_member(user=self.user, community=community, is_admin=False)
        self._add_community_member(user=another_user, community=community, is_admin=True)

        payload = {'@context': context, 'user_set':[{'@id': another_user.urlid}]}
        response = self.client.patch(f'/groups/{community.members.id}/', json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(community.members.user_set.count(), 1)

    def test_leave_circle_user_cache_updates(self):
        self.setUpLoggedInUser()
        another_user = self._get_random_user()
        community = self._get_random_community()
        community.members.user_set.add(self.user)
        community.members.user_set.add(another_user)

        response = self.client.get('/users/{}/'.format(self.user.username))
        self.assertEqual(response.status_code, 200)
        self.assertIn('communities', response.data)
        response = self.client.get(response.data['communities']['@id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['ldp:contains']), 1)

        payload = {'@context': context, 'user_set':[{'@id': another_user.urlid}]}
        response = self.client.patch('/groups/{}/'.format(community.members.pk), data=json.dumps(payload), content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/users/{}/'.format(self.user.username))
        self.assertIn('communities', response.data)
        response = self.client.get(response.data['communities']['@id'])
        self.assertEqual(len(response.data['ldp:contains']), 0)
