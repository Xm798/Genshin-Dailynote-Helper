import os
import re
import json
import datetime
from ..utils import _
from ..config import config
from .model import BaseData


def prase_info(base_data, role) -> list:
    """
    Configure the data you want to receive
    """
    result: list = []
    server = {
        'cn_gf01': _('å¤©ç©ºå² ð'),
        'cn_qd01': _('ä¸çæ  ð²'),
        'os_usa': _('ç¾æ ð¦'),
        'os_euro': _('æ¬§æ ð°'),
        'os_asia': _('äºæ ð¯'),
        'os_cht': _('å°æ¸¯æ¾³æ ð§'),
    }
    result.append(f"{role['nickname']} {server[role['region']]}")
    if config.DISPLAY_UID:
        hidden_uid = str(role['game_uid']).replace(
            str(role['game_uid'])[3:-3], '***', 1
        )
        result.append(f'UIDï¼{hidden_uid}')
    result.append('--------------------')

    if config.RESIN_INFO:
        result.append(get_resin_info(base_data))
    # resin_discount_num_limit
    if config.TROUNCE_INFO:
        result.append(get_trounce_info(base_data))
    # task_num
    if config.COMMISSION_INFO:
        result.append(get_commission_info(base_data))
    # transformer
    if config.TRANSFORMER_INFO and base_data.transformer:
        result.append(get_transformer_info(base_data))
    # home_coin
    if config.HOMECOIN_INFO:
        result.append(get_homecoin_info(base_data))
    # expedition_num
    if config.EXPEDITION_INFO:
        result.append(get_expedition_info(base_data))
    return result


def seconds2hours(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def get_resin_info(base_data: BaseData) -> str:
    resin_data = (_('å½åæ èï¼{} / {}\n')).format(
        base_data.current_resin, base_data.max_resin
    )
    if base_data.current_resin < 160:
        next_resin_rec_time = seconds2hours(
            8 * 60
            - (
                (base_data.max_resin - base_data.current_resin) * 8 * 60
                - base_data.resin_recovery_time
            )
        )
        resin_data += (_('ä¸ä¸ªåå¤åè®¡æ¶ï¼{}\n')).format(next_resin_rec_time)
        overflow_time = datetime.datetime.now() + datetime.timedelta(
            seconds=base_data.resin_recovery_time
        )
        day = _('ä»å¤©') if datetime.datetime.now().day == overflow_time.day else _('æå¤©')
        resin_data += _('å¨é¨åå¤æ¶é´ï¼{} {}').format(day, overflow_time.strftime('%X'))
    return resin_data


def get_trounce_info(base_data: BaseData) -> str:
    return _('å¨æ¬æ èååï¼{} / {}').format(
        base_data.remain_resin_discount_num, base_data.resin_discount_num_limit
    )


def get_commission_info(base_data: BaseData) -> str:
    task_num: str = f"{base_data.finished_task_num} / {base_data.total_task_num}"
    status = _('å¥å±å·²é¢å') if base_data.is_extra_task_reward_received else _('å¥å±æªé¢å')
    return _('ä»æ¥å§æä»»å¡ï¼{}   {}\n--------------------').format(task_num, status)


def get_homecoin_info(base_data: BaseData) -> str:
    week_day_dict = {
        0: _('å¨ä¸'),
        1: _('å¨äº'),
        2: _('å¨ä¸'),
        3: _('å¨å'),
        4: _('å¨äº'),
        5: _('å¨å­'),
        6: _('å¨æ¥'),
    }
    coin_data = _('å½åæ´å¤©å®é±/ä¸éï¼{} / {}\n').format(
        base_data.current_home_coin, base_data.max_home_coin
    )
    if base_data.home_coin_recovery_time:
        coin_overflow_time = datetime.datetime.now() + datetime.timedelta(
            seconds=base_data.home_coin_recovery_time
        )
        coin_data += _('æ´å¤©å®é±å¨é¨æ¢å¤æ¶é´ï¼{} {}\n').format(
            week_day_dict[coin_overflow_time.weekday()],
            coin_overflow_time.strftime('%X'),
        )
    coin_data += '--------------------'
    return coin_data


def get_expedition_info(base_data: BaseData) -> str:
    project_path = os.path.dirname(os.path.dirname(__file__))
    config_file = os.path.join(
        project_path, '', f'./locale/{config.LANGUAGE}/avatar.json'
    )
    with open(config_file, 'r', encoding='utf-8') as f:
        avatar_json = json.load(f)

    expedition_info: list[str] = []
    finished = 0
    for expedition in base_data.expeditions:
        avatar = re.search(
            r'(?<=(UI_AvatarIcon_Side_)).*(?=.png)', expedition['avatar_side_icon']
        ).group()
        try:
            avatar_name: str = avatar_json[avatar]
        except KeyError:
            avatar_name: str = avatar

        if expedition['status'] == 'Finished':
            expedition_info.append(_('  Â· {}ï¼å·²å®æ').format(avatar_name))
            finished += 1
        else:
            finish_time = datetime.datetime.now() + datetime.timedelta(
                seconds=int(expedition['remained_time'])
            )
            day = _('ä»å¤©') if datetime.datetime.now().day == finish_time.day else _('æå¤©')
            expedition_info.append(
                (_('  Â· {} å®ææ¶é´ï¼{}{}')).format(
                    avatar_name, day, finish_time.strftime('%X')
                )
            )

    expedition_num: str = (
        f'{base_data.current_expedition_num}/{finished}/{base_data.max_expedition_num}'
    )
    base_data.finished_expedition_num = finished
    expedition_data: str = '\n'.join(expedition_info)
    return (_('å½åæ¢ç´¢æ´¾é£æ»æ°/å®æ/ä¸éï¼{}\n{}')).format(expedition_num, expedition_data)


def get_transformer_info(basedata: BaseData) -> str:
    if basedata.transformer.get('obtained'):
        if basedata.transformer.get('recovery_time')['reached']:
            return _('åéè´¨åä»ªï¼å·²å°±ç»ª')
        else:
            return (_('åéè´¨åä»ªï¼ {} å¤© {} å°æ¶åå¯ç¨')).format(
                basedata.transformer.get('recovery_time')['Day'],
                basedata.transformer.get('recovery_time')['Hour'],
            )
    else:
        return _('åéè´¨åä»ªï¼ æªè·å¾')
