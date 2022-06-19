import vk_api
import requests
import json


class MemeLib:
    def __init__(self, phone_number, password, print_progress=False):
        vk_session = vk_api.VkApi(phone_number, password)
        vk_session.auth()
        if print_progress:
            print('Auth completed.')
        self._vk = vk_session.get_api()

    @staticmethod
    def download_memes(memes):
        for i, meme in enumerate(memes):
            print(f'Downloading meme {i+1}/{len(memes)}...')
            request = requests.get(meme['url'])
            # все мемы скачаются в папку parsed_memes
            open(f'parsed_memes/{i+1}.jpg', 'wb').write(request.content)
        print('Download done!')

    @staticmethod
    def parse_meme(item, author):
        meme = dict()

        meme['url'] = item['sizes'][-1]['url']
        meme['owner_id'] = item['owner_id']
        meme['album_id'] = item['album_id']

        id = item.get('user_id', item['owner_id'])
        meme['author_id'] = item.get('user_id', item['owner_id']) if id != 100 else item['owner_id']
        meme['author'] = author

        meme['likes_count'] = item['likes']['count']
        meme['id'] = item['id']

        return meme

    def get_names_by_ids(self, ids):
        group_ids = [id for id in ids if id < 0]
        user_ids = [id for id in ids if id > 0]

        id_to_name = dict()
        if len(user_ids) > 0:
            users = self._vk.users.get(user_ids=user_ids)
            for user in users:
                id_to_name[user['id']] = f'{user["first_name"]} {user["last_name"]}'

        if len(group_ids) > 0:
            groups = self._vk.groups.getById(group_ids=[abs(id) for id in group_ids])
            for group in groups:
                id_to_name[-group['id']] = group['name']

        names = [id_to_name[id] for id in ids]
        return names

    def get_memes_update(self, memes):
        photos = [f'{meme["owner_id"]}_{meme["id"]}' for meme in memes]
        items = self._vk.photos.getById(photos=photos, extended=1)
        return [self.parse_meme(items[i], memes[i]['author']) for i in range(len(photos))]

    def get_memes(self, owner_id, album_id, desired_count=-1, print_progress=False):
        if desired_count == 0:
            return list()
        elif desired_count < 0:
            check_album = self._vk.photos.get(owner_id=owner_id, album_id=album_id)
            desired_count = check_album['count']
        desired_count = min(100, desired_count)

        if print_progress:
            print('parsing memes...')
        album = self._vk.photos.get(owner_id=owner_id, album_id=album_id, count=desired_count, extended=1)
        items = album['items']

        get_author_id_by_item = lambda item: item.get('user_id', item['owner_id']) if item.get('user_id', item['owner_id']) != 100 else item['owner_id']
        authors = self.get_names_by_ids([get_author_id_by_item(item) for item in album['items']])
        assert len(items) == len(authors)

        memes = []
        for i in range(len(items)):
            if print_progress:
                print(f'parsing {i+1}/{len(album["items"])}.')
            memes.append(self.parse_meme(items[i], authors[i]))

        if print_progress:
            print('parsing memes completed.')
        return memes

    def get_memes_info(self, memes):
        for meme in memes:
            yield f'Author: {meme["author"]}, likes: {meme["likes_count"]}.'

    def set_like(self, meme):
        response = self._vk.likes.add(type='photo', owner_id=meme['owner_id'], item_id=meme['id'])