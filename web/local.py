from dataclasses import dataclass

@dataclass
class Local:
    name: str
    time: str
    master_rank: str
    skill_name: str
    flavor: str
    start: str
    over: str
    description: str
    ver: str
    ver_time: int

# local
jp_local = Local(
    name='jp_name',
    time='jp_time',
    master_rank='jp_master_rank',
    skill_name='jp_skill_name',
    flavor='jp_flavor',
    start='jp_start',
    over='jp_over',
    description='jp_description',
    ver='jp',
    ver_time=9
)
as_local = Local(
    name='as_name',
    time='as_time',
    master_rank='as_master_rank',
    skill_name='as_skill_name',
    flavor='as_flavor',
    start='as_start',
    over='as_over',
    description='as_description',
    ver='as',
    ver_time=8
)
