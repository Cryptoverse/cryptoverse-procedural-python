from __future__ import division

import json
from collections import OrderedDict
from hashlib import sha256

from procedural import generation_types

GENERATION_DATA = json.load(open('generation_data.json'), object_pairs_hook=OrderedDict)
ALL_BODIES = {
    'galaxy': GENERATION_DATA['galaxies'],
    'star': GENERATION_DATA['stars'],
    'planet': GENERATION_DATA['planets']
}


def get_attribute_hash(parent_hash, attribute_name):
    return sha256((attribute_name + parent_hash.hexdigest()).encode('ascii'))


def get_attribute(parent_hash, attribute_name, attribute_type):
    """Get attribute value from the attribute's name and type from the parent hash"""
    attribute_hash = get_attribute_hash(parent_hash, attribute_name)
    return generation_types.unpack(attribute_hash, attribute_type)


def weighed_choice(choices, choice_hash, choice_key='odds'):
    choice_list = []
    for choice_name, choice_data in choices.items():
        choice_odds = choice_data[choice_key]
        choice_list.extend([choice_name] * choice_odds)
    total_odds = len(choice_list)
    choice_i = generation_types.get_range(choice_hash, 0, total_odds - 1)
    return choice_list[choice_i]


def get_body_data(body_hash, body_type):
    attribute_name = body_type + '_type'
    choice_hash = get_attribute_hash(body_hash, attribute_name)
    all_bodies = ALL_BODIES[body_type]
    body = weighed_choice(all_bodies, choice_hash, choice_key='odds')
    return dict(all_bodies[body])


def generate_planet(planet_hash):
    planet_data = get_body_data(planet_hash, 'planet')
    has_ring_hash = get_attribute_hash(planet_hash, 'planet_has_ring')
    has_ring = generation_types.get_bool_by_chance(has_ring_hash, planet_data['ring_chance'])
    planet = {}
    planet['planet_type'] = planet_data['planet_type']
    planet['habitable'] = planet_data['habitable']
    planet['has_ring'] = has_ring
    if planet['habitable']:
        planet['climate'] = planet_data['climate']
    return planet


def generate_star(star_hash):
    star_data = get_body_data(star_hash, 'star')
    planet_count_hash = get_attribute_hash(star_hash, 'star_planet_count')
    min_planets, max_planets = star_data['min_planets'], star_data['max_planets']
    planet_count = generation_types.get_range(planet_count_hash, min_planets, max_planets)
    star = {}
    star['star_type'] = star_data['star_type']
    star['planets'] = []
    for planet_i in range(1, planet_count + 1):
        attribute_name = 'star_planet_' + str(planet_i)
        planet_hash = get_attribute_hash(star_hash, attribute_name)
        planet = generate_planet(planet_hash)
        star['planets'].append(planet)
    return star


def generate_galaxy(galaxy_hash):
    galaxy_data = get_body_data(galaxy_hash, 'galaxy')
    star_count_hash = get_attribute_hash(galaxy_hash, 'galaxy_star_count')
    min_stars, max_stars = galaxy_data['min_stars'], galaxy_data['max_stars']
    star_count = generation_types.get_range(star_count_hash, min_stars, max_stars)
    galaxy = {}
    galaxy['stars'] = []
    for star_i in range(1, star_count + 1):
        attribute_name = 'galaxy_star_' + str(star_i)
        star_hash = get_attribute_hash(galaxy_hash, attribute_name)
        star = generate_star(star_hash)
        galaxy['stars'].append(star)
    return galaxy


if __name__ == '__main__':
    import random

    galaxy_hash = sha256(str(random.random()).encode('ascii'))
    galaxy_data = generate_galaxy(galaxy_hash)
    json.dump(galaxy_data, open('sample_galaxy.json', 'w'), indent=2)
