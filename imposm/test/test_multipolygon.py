# Copyright 2011 Omniscale (http://omniscale.com)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from imposm.base import Relation, Way
from imposm.multipolygon import UnionRelationBuilder, ContainsRelationBuilder, Ring, merge_rings

from nose.tools import eq_

class RelationBuilderTestBase(object):

    def test_simple_polygon_w_hole(self):
        w1 = Way(1, {}, [1, 2, 3, 4, 1])
        w1.coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        w2 = Way(2, {}, [5, 6, 7, 8, 5])
        w2.coords = [(2, 2), (8, 2), (8, 8), (2, 8), (2, 2)]
    
        r = Relation(1, {}, [(1, 'way', 'outer'), (2, 'way', 'inner')])
        builder = self.relation_builder(r, None, None)
        rings = builder.build_rings([w1, w2])
        eq_(len(rings), 2)
        eq_(rings[0].geom.area, 100)
        eq_(rings[1].geom.area, 36)
    
        builder.build_relation_geometry(rings)
    
        eq_(r.geom.area, 100-36)

    def test_polygon_w_multiple_holes(self):
        w1 = Way(1, {}, [1, 2, 3, 4, 1])
        w1.coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        w2 = Way(2, {}, [1, 2, 3, 4, 1])
        w2.coords = [(1, 1), (2, 1), (2, 2), (1, 2), (1, 1)]
        w3 = Way(3, {}, [1, 2, 3, 4, 1])
        w3.coords = [(3, 3), (4, 3), (4, 4), (3, 4), (3, 3)]
    
        r = Relation(1, {}, [
            (1, 'way', 'outer'), (2, 'way', 'inner'), (3, 'way', 'inner')])
        builder = self.relation_builder(r, None, None)
        rings = builder.build_rings([w1, w2, w3])
        eq_(len(rings), 3)
        eq_(rings[0].geom.area, 100)
        eq_(rings[1].geom.area, 1)
        eq_(rings[2].geom.area, 1)
    
        builder.build_relation_geometry(rings)
    
        eq_(rings[0].inserted, True)
        eq_(rings[1].inserted, False)
        eq_(rings[2].inserted, False)
    
        eq_(r.geom.area, 100-1-1)


    def test_polygon_w_nested_holes(self):
        w1 = Way(1, {}, [1, 2, 3, 4, 1])
        w1.coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        w2 = Way(2, {}, [1, 2, 3, 4, 1])
        w2.coords = [(1, 1), (9, 1), (9, 9), (1, 9), (1, 1)]
        w3 = Way(3, {}, [5, 6, 7, 8, 5])
        w3.coords = [(2, 2), (8, 2), (8, 8), (2, 8), (2, 2)]
        w4 = Way(4, {}, [9, 10, 11, 12, 9])
        w4.coords = [(3, 3), (7, 3), (7, 7), (3, 7), (3, 3)]
        w5 = Way(5, {}, [9, 10, 11, 12, 9])
        w5.coords = [(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]
    
        r = Relation(1, {}, [
            (1, 'way', 'outer'), (2, 'way', 'inner'), (3, 'way', 'inner'),
            (4, 'way', 'inner'), (5, 'way', 'inner')])
        builder = self.relation_builder(r, None, None)
        rings = builder.build_rings([w1, w2, w3, w4, w5])
        eq_(len(rings), 5)
        eq_(rings[0].geom.area, 100)
        eq_(rings[1].geom.area, 64)
        eq_(rings[2].geom.area, 36)
        eq_(rings[3].geom.area, 16)
        eq_(rings[4].geom.area, 4)
    
        builder.build_relation_geometry(rings)

        eq_(rings[0].inserted, True)
        eq_(rings[1].inserted, False)
        eq_(rings[2].inserted, True)
        eq_(rings[3].inserted, False)
        eq_(rings[4].inserted, True)
    
        eq_(r.geom.area, 100-64+36-16+4)

    def test_polygon_w_touching_holes(self):
        w1 = Way(1, {}, [1, 2, 3, 4, 1])
        w1.coords = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        w2 = Way(2, {}, [1, 2, 3, 4, 1])
        w2.coords = [(1, 1), (5, 1), (5, 9), (1, 9), (1, 1)]
        w3 = Way(3, {}, [1, 2, 3, 4, 1])
        w3.coords = [(5, 1), (9, 1), (9, 9), (5, 9), (5, 1)]
    
        r = Relation(1, {}, [
            (1, 'way', 'outer'), (2, 'way', 'inner'), (3, 'way', 'inner')])
        builder = self.relation_builder(r, None, None)
        rings = builder.build_rings([w1, w2, w3])
        eq_(len(rings), 3)
        eq_(rings[0].geom.area, 100)
        eq_(rings[1].geom.area, 32)
        eq_(rings[2].geom.area, 32)
    
        builder.build_relation_geometry(rings)

        eq_(rings[0].inserted, True)
        eq_(rings[1].inserted, False)
        eq_(rings[2].inserted, False)
    
        eq_(r.geom.area, 100-64)

    def test_simple_polygon_from_two_lines(self):
        w1 = Way(1, {}, [1, 2, 3])
        w1.coords = [(0, 0), (10, 0), (10, 10)]
        w2 = Way(2, {}, [3, 4, 1])
        w2.coords = [(10, 10), (0, 10), (0, 0)]
    
        r = Relation(1, {}, [(1, 'way', 'outer'), (2, 'way', 'inner')])
        builder = self.relation_builder(r, None, None)
        rings = builder.build_rings([w1, w2])
        eq_(len(rings), 1)
        eq_(rings[0].geom.area, 100)
    
        builder.build_relation_geometry(rings)
    
        eq_(r.geom.area, 100)


class TestUnionRelationBuilder(RelationBuilderTestBase):
    relation_builder = UnionRelationBuilder


class TestContainsRelationBuilder(RelationBuilderTestBase):
    relation_builder = ContainsRelationBuilder


def test_merge_rings():
    w1 = Way(1, {}, [1, 2, 3])
    w1.coords = [(0, 0), (10, 0), (10, 10)]
    r1 = Ring(w1)
    w2 = Way(2, {}, [3, 4, 1])
    w2.coords = [(10, 10), (0, 10), (0, 0)]
    r2 = Ring(w2)
    
    rings = merge_rings([r1, r2])
    eq_(len(rings), 1)
    r = rings[0]
    eq_(r.is_closed(), True)
    # eq_(r.ways, [w1, w2])

def test_merge_rings_reverse_endpoint():
    w1 = Way(1, {'name': 'foo'}, [1, 2, 3, 4])
    w1.coords = []
    r1 = Ring(w1)
    w2 = Way(2, {'building': 'true'}, [6, 5, 4])
    w2.coords = []
    r2 = Ring(w2)
    w3 = Way(3, {}, [1, 7, 6])
    w3.coords = []
    r3 = Ring(w3)
    
    rings = merge_rings([r1, r2, r3])
    eq_(len(rings), 1)
    r = rings[0]
    eq_(r.tags, {'name': 'foo', 'building': 'true'})
    eq_(r.is_closed(), True)
    # eq_(r.ways, [w1, w2, w3])


class W(Way):
    # way without coords
    coords = []

from imposm.merge import permutations

def test_merge_rings_permutations():
    """
    Test all possible permutations of 4 ring segments.
    """
    for i in range(16):
        # test each segment in both directions
        f1 = i & 1 == 0
        f2 = i & 2 == 0
        f3 = i & 4 == 0
        f4 = i & 8 == 0
        for i1, i2, i3, i4 in permutations([0, 1, 2, 3]):
            ways = [
                W(1, {}, [1, 2, 3, 4] if f1 else [4, 3, 2, 1]),
                W(2, {}, [4, 5, 6, 7] if f2 else [7, 6, 5, 4]),
                W(3, {}, [7, 8, 9, 10] if f3 else [10, 9, 8, 7]),
                W(4, {}, [10, 11, 12, 1] if f4 else [1, 12, 11, 10]),
            ]
            ways = [ways[i1], ways[i2], ways[i3], ways[i4]]
            rings = [Ring(w) for w in ways]
            
            merged_rings = merge_rings(rings)
            eq_(len(merged_rings), 1)
            r = merged_rings[0]
            eq_(r.is_closed(), True, (ways, r.refs))
            eq_(set(r.ways), set(ways))

            # check order of refs
            prev_x = r.refs[0]
            for x in r.refs[1:]:
                if not abs(prev_x - x) == 1:
                    assert (
                        (prev_x == 1 and x == 12) or 
                        (prev_x == 12 and x == 1)
                    ), 'not in order %r' % r.refs
                prev_x = x