import uuid, json
from django.test import TestCase
from ninja.testing import TestClient
from django.contrib.auth.models import User
from pond.models import Pond
from cycle.models import Cycle
from food_sampling.models import FoodSampling
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta
from food_sampling.api import router

class FoodSamplingAPITest(TestCase):

    def setUp(self):
        date_now = datetime.now()
        start_date = date_now - timedelta(days=30)
        end_date = start_date + timedelta(days=60)

        self.client = TestClient(router)
        self.user = User.objects.create_user(username='081234567890', password='abc123')
        self.pond = Pond.objects.create(
            owner=self.user,
            name='Test Pond',
            image_name='test_pond.png',
            length=10.0,
            width=5.0,
            depth=2.0
        )
        self.pondB = Pond.objects.create(
            owner=self.user,
            name='Test Pond B',
            image_name='test_pondB.png',
            length=10.0,
            width=5.0,
            depth=2.0
        )
        self.cycle = Cycle.objects.create(
            supervisor = self.user,
            start_date = start_date,
            end_date = end_date,
        )
        self.food_sampling = FoodSampling.objects.create(
            pond=self.pond,
            reporter=self.user,
            cycle=self.cycle,
            food_quantity=1.0,
            recorded_at = datetime.now()
        )
        self.food_sampling_userA = FoodSampling.objects.create(
            pond=self.pond,
            reporter=self.user,
            cycle=self.cycle,
            food_quantity=1.5,
            recorded_at = datetime.now()
        )
    
    def test_get_food_sampling(self):
        response = self.client.get(f'/{self.cycle.id}/{self.pond.pond_id}/{self.food_sampling.sampling_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 200)
    
    def test_get_food_sampling_cycle_not_active(self): 
        start_date = datetime.now()
        end_date = start_date + timedelta(days=60)
        cycle = Cycle.objects.create(
            supervisor=self.user,
            start_date=start_date,
            end_date=end_date
        )
        response = self.client.get(f'/{cycle.id}/{self.pond.pond_id}/{self.food_sampling.sampling_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_get_food_sampling_different_cycle(self):
        starting_date = datetime.now()
        ending_date = starting_date + timedelta(days=60)
        cycle = Cycle.objects.create(
            supervisor=self.user,
            start_date=starting_date,
            end_date=ending_date
        )
        response = self.client.get(f'/{cycle.id}/{self.pond.pond_id}/{self.food_sampling.sampling_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_get_food_sampling_invalid_pond(self):
        response = self.client.get(f'/{self.cycle.id}/{uuid.uuid4()}/{self.food_sampling.sampling_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_get_food_sampling_different_pond(self):
        response = self.client.get(f'/{self.cycle.id}/{self.pondB.pond_id}/{self.food_sampling.sampling_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_get_food_sampling_invalid_food_sampling(self):
        response = self.client.get(f'/{self.cycle.id}/{self.pond.pond_id}/{uuid.uuid4()}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_get_food_sampling_invalid_user(self):
        user = User.objects.create_user(username='081234567891', password='admin1234')
        response = self.client.get(f'/{self.cycle.id}/{self.pond.pond_id}/{self.food_sampling.sampling_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(user))}"})
        self.assertEqual(response.status_code, 401)
    
    def test_list_food_samplings(self):
        response = self.client.get(f'/{self.cycle.id}/{self.pond.pond_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        expected_data = [
        {
            "sampling_id": str(self.food_sampling.sampling_id),
            "pond_id": str(self.food_sampling.pond.pond_id),
            "cycle_id": str(self.food_sampling.cycle.id),
            "reporter": str(self.food_sampling.reporter),
            "food_quantity": float(self.food_sampling.food_quantity),
            "sample_date": self.food_sampling.sample_date
        },
        {
            "sampling_id": str(self.food_sampling_userA.sampling_id),
            "pond_id": str(self.food_sampling_userA.pond.pond_id),
            "cycle_id": str(self.food_sampling_userA.cycle.id),
            "reporter": str(self.food_sampling_userA.reporter),
            "food_quantity": float(self.food_sampling_userA.food_quantity),
            "sample_date": self.food_sampling_userA.sample_date
        }
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)
    
    def test_list_food_sampling_unauthorized(self):
        response = self.client.get(f'/{self.cycle.id}/{self.pond.pond_id}/{self.food_sampling.sampling_id}/', headers={})
        self.assertEqual(response.status_code, 401)
    
    def test_list_food_sampling_by_invalid_cycle(self):
        response = self.client.get(f'{uuid.uuid4()}/{self.pond.pond_id}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_list_food_sampling_by_invalid_pond(self):
        response = self.client.get(f'/{self.cycle.id}/{uuid.uuid4()}/', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_get_latest_food_sampling(self):
        response = self.client.get(f'/{self.cycle.id}/{self.pond.pond_id}/latest', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 200)
    
    def test_get_latest_food_sampling_invalid_pond(self):
        response = self.client.get(f'/{self.cycle.id}/{uuid.uuid4()}/latest', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_get_latest_food_sampling_invalid_user(self):
        user = User.objects.create_user(username='081234567891', password='abc123')
        response = self.client.get(f'/{self.cycle.id}/{self.pond.pond_id}/latest', headers={"Authorization": f"Bearer {str(AccessToken.for_user(user))}"})
        self.assertEqual(response.status_code, 401)
    
    def test_get_latest_food_sampling_cycle_not_active(self):
        start_date = datetime.now() - timedelta(days=90)
        end_date = start_date + timedelta(days=60)
        cycle = Cycle.objects.create(
            supervisor=self.user,
            start_date=start_date,
            end_date=end_date
        )
        response = self.client.get(f'/{cycle.id}/{self.pond.pond_id}/latest', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 400)
    
    def test_get_latest_food_sampling_not_found(self):
        response = self.client.get(f'/{self.cycle.id}/{self.pondB.pond_id}/latest', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_add_food_sampling(self):
        response = self.client.post(f'/{self.cycle.id}/{self.pond.pond_id}/', data=json.dumps({
            'pond_id': str(self.pond.pond_id),  
            'reporter_id': self.user.id,
            'cycle_id': str(self.cycle.id),     
            'food_quantity': 30,
            'recorded_at': datetime.now()
        }), content_type='application/json', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 200)

    def test_add_food_sampling_with_invalid_data(self):
        response = self.client.post(f'/{self.cycle.id}/{self.pond.pond_id}/', data=json.dumps({
            'sampling_id': str(self.food_sampling.sampling_id),
            'pond_id': str(self.pond.pond_id),
            'reporter_id': self.user.id,
            'cycle_id': str(self.cycle.id),
            'food_quantity': -30,
            'recorded_at': datetime.now()
        }), content_type='application/json', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 200)
    
    def test_add_food_sampling_with_pond_not_found(self):
        response = self.client.post(f'/{self.cycle.id}/{uuid.uuid4()}/', data=json.dumps({
            'sampling_id': str(self.food_sampling.sampling_id),
            'pond_id': str(uuid.uuid4()),
            'reporter_id': self.user.id,
            'cycle_id': str(self.cycle.id),
            'food_quantity': 30,
            'recorded_at': datetime.now()
        }), content_type='application/json', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_add_food_sampling_with_cycle_not_found(self):
        response = self.client.post(f'/{uuid.uuid4()}/{self.pond.pond_id}/', data=json.dumps({
            'sampling_id': str(self.food_sampling.sampling_id),
            'pond_id': str(self.pond.pond_id),
            'reporter_id': self.user.id,
            'cycle_id': str(uuid.uuid4()),
            'food_quantity': 30,
            'recorded_at': datetime.now()
        }), content_type='application/json', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 404)
    
    def test_add_food_sampling_already_existing(self):
        response = self.client.post(f'/{self.cycle.id}/{self.pond.pond_id}/', data=json.dumps({
            'sampling_id': str(self.food_sampling.sampling_id),
            'pond_id': str(self.pond.pond_id),
            'reporter_id': self.user.id,
            'cycle_id': str(uuid.uuid4()),
            'food_quantity': 1.0,
            'recorded_at': datetime.now()
        }), content_type='application/json', headers={"Authorization": f"Bearer {str(AccessToken.for_user(self.user))}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodSampling.objects.filter(cycle=self.cycle, pond=self.pond).count(), 1)