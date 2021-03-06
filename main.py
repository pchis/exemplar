# -*- coding: utf-8 -*-

import logging

import chargen

from flask import Flask
from flask import request
from flask import Response


app = Flask(__name__)


EXPLANATORY = "\n\n" + """
===============================================================================

SPENDING BONUSES:
Every character starts with one bonus; overlapping abilities may grant you a
few extra bonuses. Each bonus may be used for one of the following. Note that
some options cost an extra raise.

    - Add a specialty to an ability rated at 3d or higher, which currently
      lacks a specialty.
    - Add a new resource, as approved by the Reeree.
    - Add a new trait without special rules, as approved by the Referee.
    - Add a new training.
    - Increase an ability from 2d to 3d, or from 3d to 4d, at the cost of
      one raise.

CALCULATING VITALITY:
Vitality is equal to your dice in Steel, plus your dice in the best of
Prowess, Speed, Stealth, and Survival. Add in any bonuses from traits.

CALCULATING GUARD VALUE:
Guard value is 1 if Prowess is 2d, or 2 if Prowess is 3d or higher. If you
have training with shields or parrying blades, you may add +1 to guard value
when properly equipped.

NOTE ON OVERLAPPING ATTRIBUTES:
Overlapping grants of character attributes are handled as follows:

    - Specialties: You may only have one specialty in each ability. If granted
      multiple specialties in an ability, choose one to keep, and lose the
      rest.
    - Training: If granted the same training multiple times, you only get it
      once. (Extra versions of the same training wouldn't help you, anyay.)
    - Traits: If granted the same trait multiple times, you only get it once.
    - Resources: You may only have one line of credit, one stipend or source
      of income, one reserve of wealth, and one lodging or source of room and
      board; for each of these categories, if you have multiple resources,
      choose one to keep and drop the rest. If you have multiple weapons and
      armor resources, merge them into one, dropping any duplicate items.
"""


@app.route('/')
def random_character():
  accept = False
  while not accept:
    ch = chargen.Character()
    accept = ch.legal and ch.power_level >= 7 and ch.power_level <= 20
  text = "{}{}".format(ch, EXPLANATORY)
  return Response(text, mimetype="text/plain; charset=unicode")


@app.route('/list')
def list_archetypes():
  sorted_archs = sorted(
      chargen.Character.ARCHETYPES,
      key=lambda a: (a.power_level, a.name))
  text = "\n".join([
    "Power Level {}".format(a.power_level).ljust(20) + a.name
    for a in sorted_archs])
  return Response(text, mimetype="text/plain")


@app.route('/search/<path:query>')
def search_archetypes(query):
  sorted_archs = sorted(
      chargen.Character.ARCHETYPES,
      key=lambda a: (a.power_level, a.name))
  matches = [a for a in sorted_archs if query.lower() in a.raw_text]
  header = "{n} archetypes contain the string '{q}'.\n\n".format(
      n=len(matches), q=query)
  text = header + "\n".join([
    "Power Level {}".format(a.power_level).ljust(20) + a.name
    for a in matches])
  return Response(text, mimetype="text/plain")


@app.route('/<path:archnames>')
def character(archnames):
  text = str(chargen.Character(*archnames.split(",")))  + EXPLANATORY
  return Response(text, mimetype="text/plain")


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
