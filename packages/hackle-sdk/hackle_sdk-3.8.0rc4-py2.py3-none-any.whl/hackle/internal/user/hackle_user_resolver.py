from hackle.internal.model.properties_builder import PropertiesBuilder
from hackle.model import User, HackleUser
from hackle.internal.user.identifier_type import IdentifierType
from hackle.internal.user.identifiers_builder import IdentifiersBuilder
from hackle.internal.user.internal_hackle_user import InternalHackleUser


class HackleUserResolver(object):

    # noinspection PyMethodMayBeStatic
    def resolve_or_none(self, user):
        """
        :param HackleUser user:
         
        :rtype: InternalHackleUser or None 
        """
        if user is None:
            return None

        if isinstance(user, User):
            hackle_user = HackleUser.of(user)
        elif isinstance(user, HackleUser):
            hackle_user = user
        else:
            return None

        user_properties = PropertiesBuilder.sanitize(hackle_user.properties)

        identifiers_builder = IdentifiersBuilder()
        identifiers_builder.add_identifiers(hackle_user.identifiers)

        if hackle_user.id is not None:
            identifiers_builder.add(IdentifierType.ID, hackle_user.id)

        if hackle_user.user_id is not None:
            identifiers_builder.add(IdentifierType.USER, hackle_user.user_id)

        if hackle_user.device_id is not None:
            identifiers_builder.add(IdentifierType.DEVICE, hackle_user.device_id)

        identifiers = identifiers_builder.build()

        if len(identifiers) == 0:
            return None

        return InternalHackleUser(identifiers, user_properties)
