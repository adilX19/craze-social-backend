from .models import User

class EmailAuthBackend(object):
	"""
	Authenticate a user using an e-mail address
	"""
	def authenticate(self, request, username=None, password=None):
		try:
			user_profile = User.objects.get(email=username)
			if user_profile.check_password(password):
				return user_profile
			return None
		except User.DoesNotExist:
			return None

	def get_user(self, user_id):
		try:
			return User.objects.get(id=user_id)
		except User.DoesNotExist:
			return None