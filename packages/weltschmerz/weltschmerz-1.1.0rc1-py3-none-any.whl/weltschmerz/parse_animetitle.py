#!/usr/bin/python3

import os.path
from weltschmerz import anime
import configparser
import argparse
import xml.etree.ElementTree as ET
import html
from sqlalchemy.orm import load_only


def get_config(config_file=os.path.expanduser("~/.config/weltschmerz/weltschmerz.cfg")):
    config = configparser.ConfigParser()
    with open(config_file, "r", encoding="UTF-8") as cf:
        config.read_file(cf)

    parser = argparse.ArgumentParser(
        description="parse and import anime titles from AniDB title dump"
    )
    parser.add_argument(
        "--database", help="database to use", default=config.get("client", "database")
    )
    parser.add_argument("--anime-title-xml", help="anime title XML file to import")

    args = parser.parse_args()
    return args


def parse_file(filename):
    anime_list = {}
    tree = ET.parse(filename)
    root = tree.getroot()
    for anime_entry in root:
        if anime_entry.attrib["aid"] not in anime_list:
            anime_list[anime_entry.attrib["aid"]] = []
        for atitle in anime_entry:
            anime_list[anime_entry.attrib["aid"]].append(
                (
                    atitle.attrib["type"],
                    atitle.attrib["{http://www.w3.org/XML/1998/namespace}lang"],
                    html.unescape(str(atitle.text)),
                )
            )
    return anime_list


def import_anime_titles(database, anime_title_xml):
    dbs = anime.DatabaseSession(database, False)
    data = parse_file(anime_title_xml)
    with dbs.session.begin():
        # title dump has all titles, delete all from DB before importing
        dbs.session.query(anime.AnimeTitle).delete()
        db_anime_list = (
            dbs.session.query(anime.Anime)
            .options(load_only(anime.Anime.aid))
            .order_by(anime.Anime.aid)
            .all()
        )

        for aid, titles in data.items():
            if int(aid) not in [a.aid for a in db_anime_list]:
                db_anime = anime.Anime(aid=int(aid))
                dbs.session.add(db_anime)
            for title_type, title_lang, title in titles:
                db_title = anime.AnimeTitle(
                    aid=aid, type=title_type, lang=title_lang, title=title
                )
                dbs.session.add(db_title)
                # print(f"{aid}, {title_type}, {title_lang}, {title}")
    dbs.session.commit()


if __name__ == "__main__":
    config = get_config()
    import_anime_titles(config.database, config.anime_title_xml)
