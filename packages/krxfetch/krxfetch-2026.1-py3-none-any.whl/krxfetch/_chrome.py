import datetime


def _release_schedule() -> tuple:
    """Chromium release schedule

    https://chromiumdash.appspot.com/schedule
    """
    schedule = (
        ('Jan 13, 2026', 144),
        ('Dec 2, 2025', 143),
        ('Oct 28, 2025', 142),
        ('Sep 30, 2025', 141),
        ('Sep 2, 2025', 140),
        ('Aug 5, 2025', 139),
        ('Jun 24, 2025', 138),
        ('May 27, 2025', 137),
        ('Apr 29, 2025', 136),
        ('Apr 1, 2025', 135),
        ('Mar 4, 2025', 134),
        ('Feb 4, 2025', 133),
        ('Jan 14, 2025', 132),
        ('Nov 12, 2024', 131)
    )

    return schedule


def _major_version(now: datetime.datetime | None = None) -> int:
    """Major version of Chrome Browser"""

    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)

    schedule = _release_schedule()
    version = schedule[len(schedule)-1][1] - 1

    for item in schedule:
        if now.date() > datetime.datetime.strptime(item[0], '%b %d, %Y').date():
            version = item[1]
            break

    return version


def _unified_platform() -> str:
    """platform part of user-agent

    macOS:   'Macintosh; Intel Mac OS X 10_15_7'
    windows: 'Windows NT 10.0; Win64; x64'
    linux:   'X11; Linux x86_64'

    https://chromium.googlesource.com/chromium/src.git/+/refs/heads/main/content/common/user_agent.cc
    """
    platform = 'Macintosh; Intel Mac OS X 10_15_7'

    return platform


def user_agent(major_ver: int | None = None) -> str:
    """Return the user-agent of Chrome Browser"""

    if major_ver is None:
        major_ver = _major_version()

    agent = 'Mozilla/5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) ' \
            'Chrome/{}.0.0.0 Safari/537.36'

    return agent.format(_unified_platform(), major_ver)
