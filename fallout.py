#!/usr/bin/env python3

import itertools

ROOMS = {r: 4 for r in 'SPECIAL'}
ROOM_IDX = {r: idx for idx, r in enumerate('SPECIAL')}

class Dweller(object):
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats

    def __repr__(self):
        return ('{0.__class__.__name__}'
                '({0.name!r}, {0.stats!r})').format(self)


def read_dweller(string):
    name = string[:-8]
    stats = []
    for stat in string[-7:]:
        if stat == '0':
            stats.append(10)
        else:
            stats.append(int(stat))
    stats = dict(zip('SPECIAL', stats))
    return Dweller(name, stats)


def state_from_file(filename='dwellers.txt'):
    state = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            room = line[-1]
            dweller = read_dweller(line[:-1])
            state[dweller] = room
    return state


def spaces(state):
    spaces = ROOMS.copy()
    for dweller in state:
        spaces[state[dweller]] -= 1
    return spaces


def available_moves(state):
    available_spaces = spaces(state)
    moves = []
    for dest_room in available_spaces:
        if available_spaces[dest_room] == 0:
            continue
        for dweller in state:
            if state[dweller] == dest_room:
                continue
            moves.append((dweller, dest_room,
                          dweller.stats[state[dweller]] - dweller.stats[dest_room]))
    return moves


def chain_moves(depth, seq, state, score):
    #if chain is None:
    #    chain = ([], state, 0)

    new_chains = [(seq, state, score)]
    for dweller, dest, diff in available_moves(state):
        new_seq = seq.copy()
        new_seq.append((dweller, state[dweller], dest, diff))

        new_state = state.copy()
        new_state[dweller] = dest

        new_score = score + diff

        new_chains.append((new_seq, new_state, new_score))

    if depth == 1:
        return new_chains
    else:
        new_new_chains = []
        for seq, state, score in new_chains:
            new_new_chains.extend(chain_moves(depth - 1, seq, state, score))
        return new_new_chains


def best_chain(depth, state):
    options = chain_moves(depth, [], state, 0)

    best_score = -1
    best_moves = None

    for moves, state, score in options:
        if score <= best_score:
            continue

        keep = True
        for dweller in state:
            if dweller.stats[state[dweller]] == 10:
                keep = False
                break
        if not keep:
            continue

        best_score = score
        best_moves = moves

    return best_moves, best_score
