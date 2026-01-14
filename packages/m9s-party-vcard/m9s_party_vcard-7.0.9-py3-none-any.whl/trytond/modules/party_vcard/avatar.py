# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

import base64
import magic
from trytond.pool import PoolMeta


class PartyAvatar(metaclass=PoolMeta):
    __name__ = 'party.party'

    def create_vcard(self):
        """ add 'photo' if avatar-image exists
        """
        vcard = super().create_vcard()
        if self.avatar and self.export_avatar:

            # identify avatar-image
            mime_type = magic.from_buffer(self.avatar, mime=True)
            if not mime_type.startswith('image/'):
                return vcard
            mime_type = mime_type[len('image/'):]

            try:
                photo = vcard.contents.get('photo', [])[0]
            except IndexError:
                photo = None

            # add avatar to vcard
            if not photo:
                photo = vcard.add('photo')
            photo.type_param = mime_type.upper()
            photo.value = base64.b64encode(self.avatar).decode("ascii")

        return vcard

# end PartyAvatar
