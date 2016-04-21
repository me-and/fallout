#!/usr/bin/env python3

import itertools
import sys

ROOMS = {r: 6 for r in 'SPECIAL'}
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
    # File should be a list of dwellers, one per line, in the following format:
    #
    #     <name> <S><P><E><C><I><A><L><currentroom>
    #
    # Where the name is basically any string by which to identify the dweller,
    # the SPECIAL scores are the single unbuffed digit score, with a score of
    # "10" represented as "0", and the current room as the letter of the stat
    # for the training room they're currently in.
    #
    # The whitespace separating the name from the stats and room can be any
    # single character other than a newline; a space or a tab is the obvious
    # choice.
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

    best_score = 0
    best_moves = []
    best_state = state

    for dweller in best_state:
        if dweller.stats[best_state[dweller]] == 10:
            best_score -= 100

    for moves, state, score in options:
        if (score < best_score or
                (score == best_score and len(moves) >= len(best_moves))):
            continue

        for dweller in state:
            if dweller.stats[state[dweller]] == 10:
                score -= 100

        if (score < best_score or
                (score == best_score and len(moves) >= len(best_moves))):
            continue

        best_score = score
        best_moves = moves
        best_state = state

    return best_moves, best_score, best_state

def state_to_file(state, filename='dwellers.txt'):
    with open(filename, 'w') as fileobj:
        for dweller in sorted(state, key=lambda x: x.name):
            room = state[dweller]
            stats = dweller.stats.copy()
            for stat in stats:
                if stats[stat] == 10:
                    stats[stat] = 0
            fileobj.write('{}\t{}{}{}{}{}{}{}{}\n'.format(dweller.name,
                                                          stats['S'],
                                                          stats['P'],
                                                          stats['E'],
                                                          stats['C'],
                                                          stats['I'],
                                                          stats['A'],
                                                          stats['L'],
                                                          room))

if __name__ == '__main__':
    depth = int(sys.argv[1])
    moves, score, state = best_chain(depth, state_from_file())
    for dweller, src, dst, mscore in moves:
        print('{}: {} -> {} ({})'.format(dweller.name,
                                         src,
                                         dst,
                                         mscore))
    print('Total: {}'.format(score))
    state_to_file(state)
