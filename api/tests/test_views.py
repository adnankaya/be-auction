from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
import decimal
import datetime
import pytz
# internals
from api.models import *


def create_superuser(username='adnan',
                     email='adnan@kaya.com',
                     password='qwert12345'):
    return User.objects.create_superuser(username, email, password)


class CustomTokenObtainPairViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_superuser()

        self.token_url = reverse('token_obtain')

    def test_token(self):
        payload = {'username': 'adnan', 'password': 'qwert12345'}

        response = self.client.post(self.token_url, data=payload)
        self.assertContains(response, 'refresh')
        self.assertContains(response, 'access')


class ItemGenerateMixin(object):
    def setUpUser(self):
        self.user = create_superuser()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def create_items(self):
        self.item1 = Item.objects.create(name='item1', description='description item1',
                                         price=decimal.Decimal('15'), close_datetime=datetime.datetime(2021, 1, 1, 5, 5, 5, tzinfo=pytz.UTC))
        self.item2 = Item.objects.create(name='item2', description='description item2',
                                         price=decimal.Decimal('25'), close_datetime=datetime.datetime(2071, 1, 2, 5, 5, 5, tzinfo=pytz.UTC))


class ItemViewSetTestCase(TestCase, ItemGenerateMixin):
    def setUp(self):
        self.setUpUser()
        self.create_items()
        item = Item.objects.first()
        self.item_retrieve_url = reverse('api:items-detail', args=[item.id])
        self.item_list_url = reverse('api:items-list')

    def test_item_list(self):
        response = self.client.get(self.item_list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn('next', response)
        self.assertIn('previous', response)
        self.assertIn('total_pages', response)
        self.assertIn('current_page', response)
        self.assertEqual(response['count'], Item.objects.count())

    def test_item_retrieve_first(self):
        response = self.client.get(self.item_retrieve_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response['id'], 1)
        self.assertEqual(Decimal(response['price']), Decimal('15'))

    def test_item_create(self):
        item_payload = {'name': 'item new', 'description': 'description item new',
                        'price': decimal.Decimal('55'),
                        'close_datetime': datetime.datetime(2121, 2, 2, 5, 5, 5, tzinfo=pytz.UTC)
                        }
        response = self.client.post(self.item_list_url, data=item_payload)
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response['name'], 'item new')
        self.assertEqual(response['id'], Item.objects.last().id)

    def test_item_update(self):
        item1_payload = {'name': 'item1 new', 'description': 'description item1 new',
                         'price': decimal.Decimal('150'),
                         'close_datetime': datetime.datetime(2021, 1, 3, 5, 5, 5, tzinfo=pytz.UTC)
                         }

        item1 = Item.objects.get(pk=1)
        response = self.client.put(self.item_retrieve_url, data=item1_payload)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(decimal.Decimal(
            response['price']), decimal.Decimal('150'))
        self.assertEqual(response.get('name'), item1_payload.get('name'))


class ImageViewSetTestCase(TestCase, ItemGenerateMixin):
    def setUp(self):
        self.setUpUser()
        self.create_items()
        self.create_images()
        first_image = Image.objects.first()
        self.image_retrieve_url = reverse(
            'api:images-detail', args=[first_image.id])
        self.image_list_url = reverse('api:images-list')

    def create_images(self):
        self.image1 = Image.objects.create(path='a.png', item=self.item1)
        self.image2 = Image.objects.create(path='b.png', item=self.item1)
        self.image3 = Image.objects.create(path='c.png', item=self.item2)

    def test_images_list(self):
        response = self.client.get(self.image_list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.__len__(), 3)

    def test_image_retrieve_first(self):
        response = self.client.get(self.image_retrieve_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.get('id'), 1)

    def test_image_create(self):
        payload = {'path': 'd.png', 'item': 1}
        response = self.client.post(self.image_list_url, data=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Item.objects.get(pk=1).images.count(), 3)
        response = response.json()
        self.assertEqual(response.get('path'), 'd.png')

    def test_image_update_first(self):
        payload = {'path': 'aaa.jpg', 'item': 2}
        response = self.client.put(self.image_retrieve_url, data=payload)
        self.assertEqual(response.status_code, 200)
        first_image = Image.objects.first()
        response = response.json()
        self.assertEqual(response.get('path'), 'aaa.jpg')
        self.assertNotEqual(first_image.path, 'a.png')
        self.assertNotEqual(first_image.item_id, 1)
        self.assertEqual(first_image.item_id, 2)


class BidViewSetTestCase(TestCase, ItemGenerateMixin):
    def setUp(self):
        self.setUpUser()
        self.create_items()
        self.create_bids()
        self.bid_list_url = reverse('api:bids-list')
        bid = Bid.objects.first()
        self.bid_receive_url = reverse('api:bids-detail', args=[bid.id])

    def create_bids(self):

        self.bid1 = Bid.objects.create(value=decimal.Decimal(self.item1.price + 1),
                                       made_by=self.user, item=self.item1)
        self.bid2 = Bid.objects.create(value=decimal.Decimal(self.item2.price + 1),
                                       made_by=self.user, item=self.item2)

    def test_bids_list(self):
        response = self.client.get(self.bid_list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response), 2)

    def test_bid_receive_newest(self):
        response = self.client.get(self.bid_receive_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response)
        response = response.json()
        self.assertEqual(response.get('made_by'), self.user.id)
        response_created_date = datetime.datetime.fromisoformat(
            response.get('created_date'))
        self.assertGreater(response_created_date,
                           Bid.objects.get(pk=1).created_date)

    def test_bid_create(self):
        user2 = create_superuser('admin', 'admin@kaya.com', 'password')
        self.client.force_authenticate(user=user2)
        # late bidding for item 1
        payload_late = {'value': self.item1.price + 5,
                        'item': self.item1.id, 'made_by': user2.id
                        }
        response = self.client.post(self.bid_list_url, data=payload_late)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        result = any(i in response[0] for i in ['late', 'closed'])
        self.assertTrue(result)
        # success bidding for item 2
        payload_success = {'value': self.item2.price + 5,
                           'item': self.item2.id, 'made_by': user2.id}
        response = self.client.post(self.bid_list_url, data=payload_success)
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(decimal.Decimal(response.get('value')),
                         payload_success.get('value'))


class AutoBidViewSetTestCase(TestCase, ItemGenerateMixin):
    def setUp(self):
        self.setUpUser()
        self.create_items()
        self.create_autobids()
        autobid = AutoBid.objects.first()
        self.autobid_receive_url = reverse(
            'api:autobids-detail', args=[autobid.id])
        self.autobid_list_url = reverse('api:autobids-list')

    def create_autobids(self):
        self.autobid1 = AutoBid.objects.create(made_by=self.user, is_active=True,
                                               item=self.item1, max_bid_value=100)
        self.autobid2 = AutoBid.objects.create(made_by=self.user, is_active=True,
                                               item=self.item2, max_bid_value=200)

    def test_autobids_list(self):
        response = self.client.get(self.autobid_list_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response), 2)
        self.assertTrue(all(bool(bid.get('item_name')) for bid in response))

    def test_autobid_receive(self):
        response = self.client.get(self.autobid_receive_url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.get('id'), 1)
        self.assertEqual(response.get('item'), 1)
        self.assertEqual(response.get('item_name'), 'item1')

    def test_autobid_create_failed(self):
        payload_fail = {'made_by': self.user.id, 'is_active': True,
                        'item': self.item2.id, 'max_bid_value': 200}
        response = self.client.post(self.autobid_list_url, data=payload_fail)
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertDictEqual(response, {'non_field_errors': [
                             'The fields made_by, item must make a unique set.']})

    def test_autobid_create_succeeded(self):
        user2 = create_superuser('admin', 'admin@kaya.com', 'password')
        self.client.force_authenticate(user=user2)
        payload_success = {'made_by': user2.id, 'is_active': True,
                           'item': self.item2.id, 'max_bid_value': 300}
        response = self.client.post(
            self.autobid_list_url, data=payload_success)
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response.get('item'), 2)
        self.assertEqual(response.get('made_by'), 2)

    # TODO
    # unittest for auto bidding

    def test_autobid_update_first(self):
        payload = {'is_active': False, 'max_bid_value': 300}
        response = self.client.put(self.autobid_receive_url, data=payload)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.get('is_active'), False)
        self.assertEqual(decimal.Decimal(response.get(
            'max_bid_value')), decimal.Decimal(300))
        
