from meme_lib import MemeLib
import random
import constants


def rate_meme(meme, show_index=False, meme_index=-1):
    meme_index_text = f'Meme {meme_index + 1}/{len(memes)}.'
    author_text = f'Author: {meme["author"]}'
    if show_index:
        print(meme_index_text, author_text, sep=' ')
    else:
        print(author_text)
    print(f'Image: {meme["url"]}')
    print(f'0 - skip, 1 - like, 2 - exit')

    while True:
        user_input = input().strip()
        if user_input == '0':
            break
        elif user_input == '1':
            ml.set_like(meme)
            break
        elif user_input == '2':
            return 'stop'
        else:
            print('Input is incorrect. Please, try again')
            continue

def rate_memes(memes, show_index=False):
    for i, meme in enumerate(memes):
        status = rate_meme(meme, show_index=show_index, meme_index=i)
        if status == 'stop':
            return


def smart_rate_memes(memes, preferred_meme_i):
    preferred_meme = memes[preferred_meme_i]
    rival_memes = [meme for meme in memes if meme['likes_count'] >= preferred_meme['likes_count']]
    non_rival_memes = [meme for meme in memes if meme not in rival_memes]

    while True:
        statuses = []
        if random.random() < 0.1:
            status = rate_meme(preferred_meme)
            statuses.append(status)
        else:
            if random.random() < 0.75:
                status = rate_meme(random.choice(non_rival_memes))
                statuses.append(status)
            else:
                status = rate_meme(random.choice(rival_memes))
                statuses.append(status)

        if 'stop' in statuses:
            return


def watch_for_likes(memes):
    while True:
        refreshed_memes = ml.get_memes_update(memes)
        found = False
        for meme, refreshed_meme in zip(memes, refreshed_memes):
            likes_delta = refreshed_meme['likes_count'] - meme['likes_count']
            if likes_delta != 0:
                print(f'{likes_delta:+g} on meme {refreshed_meme["url"]}')
                found = True
        if not found:
            print(f'No new likes...')
        memes = refreshed_memes


def print_top_memes(count, memes):
    sorted_memes = sorted(memes, key=lambda meme: meme['likes_count'], reverse=True)
    count = min(count, len(sorted_memes))
    for meme in sorted_memes[:count]:
        print(f'Likes: {meme["likes_count"]:}, meme: {meme["url"]}')


ml = MemeLib(constants.phone_number, constants.password, print_progress=True)
memes = ml.get_memes(constants.vezdekod_owner_id, constants.vezdekod_album_id, print_progress=True)


while True:
    print('Enter command:')
    print('1 - download memes')
    print('2 - print memes info')
    print('3 - rate memes')
    print('4 - smart rate memes')
    print('5 - add another bunch of memes')
    print('6 - watch for new likes')
    print('7 - print top memes')
    print('8 - exit')
    user_input = input().strip()

    if user_input == '1':
        ml.download_memes(memes)
        continue
    elif user_input == '2':
        for meme_info in ml.get_memes_info(memes):
            print(meme_info)
        continue
    elif user_input == '3':
        rate_memes(memes, show_index=True)
        continue
    elif user_input == '4':
        smart_rate_memes(memes, 0)
        continue
    elif user_input == '5':
        add_memes = ml.get_memes(constants.gamedev_owner_id, constants.gamedev_album_id, desired_count=20, print_progress=True)
        memes += add_memes
        print('Added new memes to collection! You can download them.')
        continue
    elif user_input == '6':
        watch_for_likes(memes)
        continue
    elif user_input == '7':
        print_top_memes(10, memes)
        continue
    elif user_input == '8':
        break
    elif user_input == '9':
        for meme in memes:
            print(meme)
    else:
        print('Input is incorrect. Please, try again.')
        continue

