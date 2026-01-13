from datetime import date, datetime
from sqlite3 import Connection

from aiohttp import web

from raphson_mp.common import util
from raphson_mp.server import charts, track
from raphson_mp.server.auth import User
from raphson_mp.server.charts import StatsPeriod
from raphson_mp.server.decorators import route
from raphson_mp.server.response import template


@route("", redirect_to_login=True)
async def route_stats(_request: web.Request, conn: Connection, _user: User):
    years = [
        row[0]
        for row in conn.execute("SELECT DISTINCT strftime('%Y', timestamp, 'unixepoch', 'localtime') FROM history")
    ]
    return await template("stats.jinja2", years=years, chart_count=len(charts.CHARTS))


@route("/data/{chart}")
async def route_stats_data(request: web.Request, _conn: Connection, _user: User):
    try:
        period = StatsPeriod.from_name(request.query["period"])

    except ValueError:
        raise web.HTTPBadRequest(reason="invalid period")
    chart_id = int(request.match_info["chart"])
    data = await charts.get_chart(chart_id, period)
    if data is None:
        raise web.HTTPNoContent(reason="not enough data")
    return web.json_response(data)


@route("/recap", redirect_to_login=True)
async def recap(_request: web.Request, conn: Connection, user: User):
    today = date.today()
    year = today.year if today.month >= 11 else today.year - 1
    from_timestamp = int(datetime(year, 1, 1, 0, 0).timestamp())
    to_timestamp = int(datetime(year, 12, 31, 23, 59).timestamp())
    previous_from_timestamp = int(datetime(year - 1, 1, 1, 0, 0).timestamp())
    previous_to_timestamp = int(datetime(year - 1, 12, 31, 23, 59).timestamp())

    # Play duration is not really accurate. Deleted tracks are not counted, making the total duration
    # lower than the true duration. On the other hand, a track is considered played without completely
    # playing it through, making the total duration higher than the true direction.
    (play_count, play_duration) = conn.execute(
        """
        SELECT COUNT(*), SUM(DURATION)
        FROM history LEFT JOIN track ON history.track = track.path
        WHERE user = ? AND timestamp > ? and timestamp < ?
        """,
        (user.user_id, from_timestamp, to_timestamp),
    ).fetchone()

    (previous_play_count,) = conn.execute(
        "SELECT COUNT(*) FROM history WHERE user = ? AND timestamp > ? and timestamp < ?",
        (user.user_id, previous_from_timestamp, previous_to_timestamp),
    ).fetchone()

    result = conn.execute(
        """
        SELECT artist, COUNT(*)
        FROM history
            INNER JOIN track ON history.track = track.path
            INNER JOIN track_artist ON track_artist.track = track.path
        WHERE user = ? AND history.timestamp > ? AND history.timestamp < ?
        GROUP BY artist
        ORDER BY COUNT(*) DESC
        LIMIT 10
        """,
        (user.user_id, from_timestamp, to_timestamp),
    )

    artists = [{"name": row[0], "count": row[1], "image": f"/artist/{util.urlencode(row[0])}/image"} for row in result]

    result = conn.execute(
        """
        SELECT album, COUNT(*), track
        FROM history
            INNER JOIN track ON history.track = track.path
        WHERE user = ? AND album IS NOT NULL AND history.timestamp > ? AND history.timestamp < ?
        GROUP BY album
        ORDER BY COUNT(*) DESC
        LIMIT 10
        """,
        (user.user_id, from_timestamp, to_timestamp),
    )

    albums = [
        {"name": row[0], "count": row[1], "image": f"/track/{util.urlencode(row[2])}/cover?quality=low"}
        for row in result
    ]

    result = conn.execute(
        """
        SELECT track, COUNT(*)
        FROM history
            INNER JOIN track ON history.track = track.path
        WHERE user = ? AND history.timestamp > ? AND history.timestamp < ?
        GROUP BY track
        ORDER BY COUNT(*) DESC
        LIMIT 10
        """,
        (user.user_id, from_timestamp, to_timestamp),
    )

    tracks = [
        {
            "name": (await track.get_track(conn, row[0])).display_title(show_album=False, show_year=False),
            "count": row[1],
            "image": f"/track/{util.urlencode(row[0])}/cover?quality=low",
        }
        for row in result
    ]

    for lst in [artists, albums, tracks]:
        for _i in range(10 - len(lst)):
            lst.append({"name": "", "count": 0, "image": "/static/img/raphson_small.webp"})

    if user.primary_playlist:
        you_your_playlist = conn.execute(
            """
            SELECT
                (SELECT COUNT(*)*100 FROM history WHERE user = :user AND history.timestamp > :from AND history.timestamp < :to AND playlist = :playlist)
                /
                (SELECT COUNT(*) FROM history WHERE user = :user AND history.timestamp > :from AND history.timestamp < :to)
            """,
            {"user": user.user_id, "from": from_timestamp, "to": to_timestamp, "playlist": user.primary_playlist},
        ).fetchone()[0]

        others_your_playlist = conn.execute(
            f"""
            SELECT
                (SELECT COUNT(*)*100 FROM history WHERE user != :user AND history.timestamp > :from AND history.timestamp < :to AND playlist = :playlist)
                /
                (SELECT COUNT(*) FROM history WHERE user != :user AND history.timestamp > :from AND history.timestamp < :to)
            """,
            {"user": user.user_id, "from": from_timestamp, "to": to_timestamp, "playlist": user.primary_playlist},
        ).fetchone()[0]
    else:
        you_your_playlist = None
        others_your_playlist = None

    return await template(
        "stats_recap.jinja2",
        year=year,
        artists=artists,
        albums=albums,
        tracks=tracks,
        play_count=play_count,
        play_hours=play_duration // 3600,
        previous_play_count=previous_play_count,
        you_your_playlist=you_your_playlist,
        others_your_playlist=others_your_playlist,
    )
