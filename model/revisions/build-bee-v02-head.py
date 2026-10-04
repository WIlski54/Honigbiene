"""Reproducible, editable first model study. Run with Blender --background --python.

Axes: X longitudinal (head negative), Y lateral, Z dorsal. Anatomical placement
is a reconstruction guided by COLOSS BEEBOOK plates 8–12, not specimen CT data.
All units are normalized model units, not an asserted biological measurement.
"""
import bpy
import math
import random
import json
import sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon

random.seed(20261003)
MOBILE = '--mobile' in sys.argv
SUFFIX = '-mobile' if MOBILE else ''
DETAIL = .38 if MOBILE else 1
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'public' / 'models'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for data in list(bpy.data.materials):
    bpy.data.materials.remove(data)


def material(name, color, roughness=.4, metal=0, alpha=1):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, alpha)
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, alpha)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metal
    p.inputs['IOR'].default_value = 1.46
    if alpha < 1:
        p.inputs['Alpha'].default_value = alpha
    return m


chitin = material('Cuticle · dark umber', (.019, .009, .004), .29)
joint_mat = material('Articulations · polished cuticle', (.015, .007, .003), .25)
amber = material('Cuticle margins · amber', (.36, .13, .025), .36)
eye_mat = material('Compound eyes · lenses', (.018, .011, .008), .21)
eye_facet_mat = material('Compound eyes · facet variation', (1, 1, 1), .26)
eye_color = eye_facet_mat.node_tree.nodes.new('ShaderNodeVertexColor')
eye_color.layer_name = 'Color'
eye_facet_mat.node_tree.links.new(eye_color.outputs['Color'], eye_facet_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
mandible_mat = material('Mandibles · reddish cuticle', (.040, .013, .005), .30)
vein_mat = material('Wing veins · honey amber', (.42, .18, .042), .29)
fine_vein = material('Wing microstructure', (.68, .43, .16), .52)
wing_mat = material('Wing membrane', (.91, .85, .68), .23, alpha=.28)
wing_mat.use_backface_culling = False
hair_mat = material('Setae · vertex colour', (1, 1, 1), .68)
attr = hair_mat.node_tree.nodes.new('ShaderNodeVertexColor')
attr.layer_name = 'Color'
hair_mat.node_tree.links.new(attr.outputs['Color'], hair_mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
pollen_mat = material('Pollen · ochre', (.96, .55, .055), .85)
gut_mat = material('Midgut · illustrative olive', (.070, .14, .028), .53)
foregut_mat = material('Foregut · rose tissue', (.42, .15, .10), .48)
rectum_mat = material('Hindgut · warm tissue', (.38, .22, .067), .54)
crop_mat = material('Crop · illustrative rose', (.40, .13, .10), .39)
muscle_mat = material('Flight muscles · fibres', (.43, .16, .090), .63)
neural_mat = material('Nervous system · ivory', (.68, .45, .11), .54)
trachea_mat = material('Tracheal system · pearl', (.80, .80, .70), .40)
air_sac_mat = material('Air sacs · translucent membrane', (.73, .77, .69), .48, alpha=.22)
heart_mat = material('Dorsal vessel · tissue', (.47, .071, .040), .55)
gland_mat = material('Glands · soft tissue', (.86, .69, .42), .57)
excretory_mat = material('Malpighian tubules · illustrative slate', (.075, .18, .24), .50)

PARTS = []


def part(name, kind, offset=(0, 0, 0), start=.1, end=.55, organ=False):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj['studyPart'] = True
    obj['category'] = kind
    obj['organ'] = organ
    obj['explosion'] = {'start': start, 'end': end, 'dx': offset[0], 'dy': offset[1], 'dz': offset[2]}
    obj['anatomyStatus'] = 'reference-guided reconstruction; not yet validated'
    PARTS.append(obj)
    return obj


class Mesh:
    def __init__(self):
        self.vertices, self.faces, self.colors, self.uv = [], [], [], []

    def vertex(self, p, color=(1, 1, 1, 1), uv=(0, 0)):
        self.vertices.append(tuple(p))
        self.colors.append(color)
        self.uv.append(uv)
        return len(self.vertices) - 1

    def tube(self, points, radii, sides=7, color=None):
        points = [Vector(p) for p in points]
        rows = []
        for i, p in enumerate(points):
            tangent = (points[min(i + 1, len(points) - 1)] - points[max(0, i - 1)]).normalized()
            ref = Vector((0, 0, 1)) if abs(tangent.z) < .93 else Vector((0, 1, 0))
            a = tangent.cross(ref).normalized()
            b = tangent.cross(a).normalized()
            r = radii[i] if isinstance(radii, (list, tuple)) else radii
            col = color[i] if color else (1, 1, 1, 1)
            row = [self.vertex(p + r * (a * math.cos(j * math.tau / sides) + b * math.sin(j * math.tau / sides)), col, (i / max(1, len(points) - 1), j / sides)) for j in range(sides)]
            rows.append(row)
        for i in range(len(rows) - 1):
            for j in range(sides):
                k = (j + 1) % sides
                self.faces.append((rows[i][j], rows[i][k], rows[i + 1][k], rows[i + 1][j]))
        self.faces.append(tuple(reversed(rows[0])))
        self.faces.append(tuple(rows[-1]))

    def sphere(self, center, scale, nu=24, nv=14):
        c = Vector(center)
        rows = []
        for i in range(nv + 1):
            t = math.pi * i / nv
            row = []
            for j in range(nu + 1):
                a = math.tau * j / nu
                p = c + Vector((scale[0] * math.sin(t) * math.cos(a), scale[1] * math.sin(t) * math.sin(a), scale[2] * math.cos(t)))
                row.append(self.vertex(p, uv=(j / nu, i / nv)))
            rows.append(row)
        for i in range(nv):
            for j in range(nu):
                self.faces.append((rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1]))

    def shaped_sphere(self, surface, nu=48, nv=32):
        rows = []
        for i in range(nv + 1):
            theta = math.pi * i / nv
            rows.append([self.vertex(surface(Vector((math.sin(theta)*math.cos(j*math.tau/nu), math.sin(theta)*math.sin(j*math.tau/nu), math.cos(theta)))), uv=(j/nu, i/nv)) for j in range(nu + 1)])
        for i in range(nv):
            for j in range(nu):
                self.faces.append((rows[i][j], rows[i+1][j], rows[i+1][j+1], rows[i][j+1]))

    def flattened_tube(self, points, widths, thicknesses, sides=12, reference=(0, 1, 0)):
        points = [Vector(p) for p in points]
        rows = []
        for i, p in enumerate(points):
            tangent = (points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
            a = tangent.cross(Vector(reference)).normalized()
            b = tangent.cross(a).normalized()
            rows.append([self.vertex(p+a*widths[i]*math.cos(j*math.tau/sides)+b*thicknesses[i]*math.sin(j*math.tau/sides),uv=(i/max(1,len(points)-1),j/sides)) for j in range(sides)])
        for i in range(len(rows)-1):
            for j in range(sides):
                k=(j+1)%sides
                self.faces.append((rows[i][j],rows[i][k],rows[i+1][k],rows[i+1][j]))
        self.faces.extend([tuple(reversed(rows[0])),tuple(rows[-1])])

    def finish(self, name, mat, parent=None, colored=False, smooth=True):
        if not self.vertices:
            return None
        data = bpy.data.meshes.new(name)
        data.from_pydata(self.vertices, [], self.faces)
        data.materials.append(mat)
        data.update()
        for f in data.polygons:
            f.use_smooth = smooth
        uv = data.uv_layers.new(name='UVMap')
        for loop in data.loops:
            uv.data[loop.index].uv = self.uv[loop.vertex_index]
        if colored:
            ca = data.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='POINT')
            for i, col in enumerate(self.colors):
                ca.data[i].color = col
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.parent = parent
        return obj


def bezier(p0, p1, p2, p3, steps=24):
    p0, p1, p2, p3 = map(Vector, (p0, p1, p2, p3))
    return [(1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3 for t in [i / steps for i in range(steps + 1)]]


def ellipse_surface(c, r, t, a):
    return Vector((c[0] + r[0] * math.cos(t), c[1] + r[1] * math.sin(t) * math.cos(a), c[2] + r[2] * math.sin(t) * math.sin(a)))


def head_surface(c, r, t, a):
    # Frontal macro references: broad upper capsule, tapered cheeks and a
    # flatter face. Preserve the original dorsal/ventral explosion boundary.
    unit = Vector((math.cos(t),math.sin(t)*math.cos(a),math.sin(t)*math.sin(a)))
    front = -abs(unit.x)**.72 if unit.x < 0 else unit.x
    cheek_width = .72 + .34*(unit.z+1)*.5
    return Vector((c[0]+r[0]*front,c[1]+r[1]*unit.y*cheek_width,c[2]+r[2]*unit.z))


def surface_normal(surface,c,r,t,a):
    epsilon=.0002
    dt=surface(c,r,t+epsilon,a)-surface(c,r,t-epsilon,a)
    da=surface(c,r,t,a+epsilon)-surface(c,r,t,a-epsilon)
    n=dt.cross(da).normalized()
    if n.dot(surface(c,r,t,a)-Vector(c))<0: n=-n
    return n


def ellipse_shell(c, r, a0, a1, mat, parent, name, surface=ellipse_surface):
    mesh = Mesh()
    nx, na, wall = (32, 42, .035) if MOBILE else (48, 64, .035)
    grids = []
    for inner in (False, True):
        rr = tuple(v - wall if inner else v for v in r)
        rows = []
        for i in range(nx + 1):
            t = .015 + (math.pi - .03) * i / nx
            rows.append([mesh.vertex(surface(c, rr, t, a0 + (a1 - a0) * j / na), uv=(i / nx, j / na)) for j in range(na + 1)])
        grids.append(rows)
        for i in range(nx):
            for j in range(na):
                face = (rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1])
                mesh.faces.append(tuple(reversed(face)) if inner else face)
    for i in range(nx):
        for j in (0, na):
            mesh.faces.append((grids[0][i][j], grids[1][i][j], grids[1][i + 1][j], grids[0][i + 1][j]))
    for i in (0, nx):
        for j in range(na):
            mesh.faces.append((grids[0][i][j], grids[0][i][j + 1], grids[1][i][j + 1], grids[1][i][j]))
    return mesh.finish(name, mat, parent)


def hair(mesh, p, normal, length, gold=True, radius=.0033, branch=False, flow=None, tint=None):
    n = normal.normalized()
    jitter = Vector((random.uniform(-.55, .55), random.uniform(-.55, .55), random.uniform(-.2, .3)))
    direction = (n + jitter).normalized() if flow is None else (n*.38 + flow + jitter*.22).normalized()
    bend = Vector((random.uniform(-.025, .025), random.uniform(-.025, .025), random.uniform(-.01, .02)))
    pts = [p + n * .003, p + direction * length * .37, p + direction * length * .73 + bend * .45, p + direction * length + bend]
    variation = random.uniform(.75, 1.15)
    tip = (.56 * variation, .29 * variation, .060 * variation, 1) if gold else (.10 * variation, .041 * variation, .010 * variation, 1)
    if tint: tip=tuple(value*variation for value in tint)+(1,)
    colors = [(.15, .075, .02, 1), tuple(v * .7 if j < 3 else v for j, v in enumerate(tip)), tip, tip]
    mesh.tube(pts, [radius, radius * .85, radius * .48, .00035], sides=3, color=colors)
    if branch:
        for side in (-1, 1):
            twig = (direction + Vector((side * .7, side * .3, .2))).normalized()
            mesh.tube([pts[2], pts[2] + twig * length * .24], [radius * .45, .0003], 3, [tip, tip])


def ellipse_fur(c, r, a0, a1, count, parent, name, torso=False, surface=ellipse_surface):
    mesh = Mesh()
    for _ in range(int(count*DETAIL)):
        t = math.acos(random.uniform(-.99, .99))
        a = random.uniform(a0, a1)
        p = surface(c, r, t, a)
        n = surface_normal(surface,c,r,t,a)
        bald = torso and abs(p.x - c[0]) < .42 and abs(p.y) < .38 and p.z > c[2] + .57
        length = random.uniform(.12, .29) if torso else random.uniform(.07, .17)
        if bald:
            length *= .26
        if surface is head_surface:
            facial=p.x<c[0]-.24 and p.z<c[2]+.48
            length=random.uniform(.025,.074) if facial else random.uniform(.085,.20)
            flow=Vector((-.05, .35 if p.y>0 else -.35, -.55)) if facial else Vector((-.20, .25 if p.y>0 else -.25, .43))
            tint=(.43,.32,.14) if facial else None
            hair(mesh,p,n,length,radius=.0017,branch=random.random()<.18,flow=flow,tint=tint)
        else:
            hair(mesh, p, n, length, not bald, radius=.0025, branch=random.random() < .10)
    return mesh.finish(name, hair_mat, parent, colored=True)


def pollen_on_ellipse(c, r, count, parent, name, surface=ellipse_surface):
    mesh = Mesh()
    for _ in range(int(count*(.55 if MOBILE else 1))):
        p = surface(c, r, math.acos(random.uniform(-.96, .96)), random.uniform(0, math.pi))
        rad = random.uniform(.004, .013)
        start = len(mesh.vertices)
        for v in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            mesh.vertex(p + Vector(v) * rad)
        for face in ((0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)):
            mesh.faces.append(tuple(start + i for i in face))
    mesh.finish(name, pollen_mat, parent, smooth=False)


print('Building body shells and setae...', flush=True)
head_c, head_r = (-1.67, 0, .04), (.55, .61, .73)
thorax_c, thorax_r = (-.57, 0, .02), (.83, .76, .80)
head_upper = part('head_dorsal_capsule', 'shell', (-.22, 0, 1.42), .16, .55)
head_lower = part('head_ventral_capsule', 'shell', (-.25, 0, -.42), .2, .55)
thorax_upper = part('thorax_dorsal_cuticle', 'shell', (-.07, 0, 1.66), .13, .52)
thorax_lower = part('thorax_ventral_cuticle', 'shell', (0, 0, -.64), .2, .55)
for c, r, upper, lower, name, count in ((head_c, head_r, head_upper, head_lower, 'head', 4000), (thorax_c, thorax_r, thorax_upper, thorax_lower, 'thorax', 10000)):
    surface=head_surface if name=='head' else ellipse_surface
    ellipse_shell(c, r, 0, math.pi, chitin, upper, name + '_roof',surface)
    ellipse_shell(c, r, math.pi, math.tau, chitin, lower, name + '_floor',surface)
    ellipse_fur(c, r, 0, math.pi, int(count*.60), upper, name+'_dorsal_setae', name=='thorax',surface)
    ellipse_fur(c, r, math.pi, math.tau, int(count*.40), lower, name+'_ventral_setae', name=='thorax',surface)
    pollen_on_ellipse(c, r, 350 if name=='head' else 650, upper, name+'_pollen',surface)


def abdomen_profile(x):
    u = (x - .18) / 2.66
    radius = max(.025, math.sin(math.pi * min(.998, max(.002, u))) ** .69)
    return (.84 * radius, .68 * radius, -.055 - .14 * u)


def abdomen_point(x, a, inset=0):
    ry, rz, z = abdomen_profile(x)
    return Vector((x, (ry - inset) * math.cos(a), z + (rz - inset) * math.sin(a)))


def abdomen_plate(x0, x1, a0, a1, parent, name):
    m = Mesh()
    grids, nx, na = [], 14, 52
    for inset in (0, .027):
        rows = []
        for i in range(nx+1):
            x = x0 + (x1-x0)*i/nx
            rows.append([m.vertex(abdomen_point(x, a0+(a1-a0)*j/na, inset), uv=(i/nx,j/na)) for j in range(na+1)])
        grids.append(rows)
        for i in range(nx):
            for j in range(na):
                face = (rows[i][j], rows[i][j+1], rows[i+1][j+1], rows[i+1][j])
                m.faces.append(tuple(reversed(face)) if inset else face)
    for i in range(nx):
        for j in (0,na):
            m.faces.append((grids[0][i][j],grids[0][i+1][j],grids[1][i+1][j],grids[1][i][j]))
    for i in (0,nx):
        for j in range(na):
            m.faces.append((grids[0][i][j],grids[1][i][j],grids[1][i][j+1],grids[0][i][j+1]))
    m.finish(name, chitin, parent)
    rim = Mesh()
    rim.tube([abdomen_point(x1-.005,a0+(a1-a0)*j/80) for j in range(81)], .012, 6)
    rim.finish(name+'_posterior_rim',amber,parent)
    fur = Mesh()
    for _ in range(int((1250 if a0==0 else 650)*DETAIL)):
        x = random.uniform(x0,x1)
        a = random.uniform(a0,a1)
        p = abdomen_point(x,a)
        n = Vector((.14*(x-1.25), math.cos(a), math.sin(a)))
        band = (x-x0)/(x1-x0) > .68
        hair(fur,p,n,random.uniform(.075,.15) if band else random.uniform(.04,.08),gold=band, radius=.0027,branch=random.random()<.06)
    fur.finish(name+'_setae',hair_mat,parent,colored=True)


bounds = [.22,.69,1.18,1.66,2.09,2.45,2.81]
for i in range(6):
    upper = part(f'abdomen_tergite_{i+1}', 'shell', ((i-2.5)*.045,0,1.45+.07*i), .14+.016*i, .55)
    lower = part(f'abdomen_sternite_{i+1}', 'shell', ((i-2.5)*.025,0,-.69-.025*i), .24, .55)
    abdomen_plate(bounds[i],bounds[i+1]+(.018 if i<5 else 0),0,math.pi,upper,f'tergite_{i+1}')
    abdomen_plate(bounds[i],bounds[i+1]+(.018 if i<5 else 0),math.pi,math.tau,lower,f'sternite_{i+1}')

print('Building optical and sensory surfaces...', flush=True)
for side in (-1,1):
    eyes = Mesh()
    center = Vector((-1.83,side*.465,.13))
    scale = Vector((.275,.192,.475))
    def eye_surface(d):
        taper=.94+.10*d.z
        return center+Vector((scale.x*d.x*taper+.045*d.z,scale.y*d.y,scale.z*d.z))
    eye_base = Mesh()
    eye_base.shaped_sphere(eye_surface,64,48)
    eye_base.finish(f'compound_eye_base_{side}',eye_mat,head_lower)
    # Thousands of individually raised six-sided lenses on an ellipsoid.
    eye_rings = 36 if MOBILE else 72
    for i in range(1,eye_rings):
        theta = math.pi*i/eye_rings
        nring = max(6,int((56 if MOBILE else 112)*math.sin(theta)))
        for j in range(nring):
            phi = math.tau*(j+(.5 if i%2 else 0))/nring
            d = Vector((math.sin(theta)*math.cos(phi),math.sin(theta)*math.sin(phi),math.cos(theta)))
            a = d.cross(Vector((0,0,1))).normalized()
            b = d.cross(a).normalized()
            root = len(eyes.vertices)
            shade=random.uniform(.84,1.16)
            color=(.017*shade,.010*shade,.006*shade,1)
            eyes.vertex(eye_surface(d)+(eye_surface(d)-center)*.003,color)
            radius = .053 if MOBILE else .027
            for k in range(6):
                dd = (d + radius*(a*math.cos(k*math.tau/6)+b*math.sin(k*math.tau/6))).normalized()
                eyes.vertex(eye_surface(dd),color)
            for k in range(6):
                eyes.faces.append((root,root+1+k,root+1+(k+1)%6))
    eyes.finish(f'compound_eye_{side}',eye_facet_mat,head_lower,colored=True,smooth=False)
    ocular_setae = Mesh()
    for _ in range(int(600*DETAIL)):
        t,a = random.uniform(.2,math.pi-.2),random.uniform(0,math.tau)
        d = Vector((math.sin(t)*math.cos(a),math.sin(t)*math.sin(a),math.cos(t)))
        if d.y*side<.12: continue
        p = eye_surface(d)
        hair(ocular_setae,p,d,random.uniform(.030,.073),gold=False,radius=.0010,flow=Vector((-.16,side*.30,-.35)),tint=(.22,.15,.05))
    ocular_setae.finish(f'eye_setae_{side}',hair_mat,head_lower,colored=True)

ocelli = Mesh()
for p in ((-1.66,0,.788),(-1.43,-.18,.698),(-1.43,.18,.698)):
    ocelli.sphere(p,(.075,.067,.055),28,16)
ocelli.finish('three_ocelli',eye_mat,head_upper)

for side in (-1,1):
    antenna = part(f'antenna_{side}','appendage',(-.1,side*.32,.04),.3,.8)
    base=Vector((-2.08,side*.29,.22))
    elbow=Vector((-2.42,side*.58,.47))
    end=Vector((-3.13,side*.91,.38)) if side==1 else Vector((-2.89,-1.27,.12))
    m=Mesh(); m.tube([base,base.lerp(elbow,.5),elbow],[.046,.041,.033],12)
    m.sphere(base,(.055,.055,.055),20,12)
    m.finish(f'antenna_scape_{side}',joint_mat,antenna)
    m=Mesh(); rings=Mesh()
    for i in range(11):
        a=elbow.lerp(end,i/11); b=elbow.lerp(end,(i+1)/11)
        m.tube([a.lerp(b,.04),a.lerp(b,.96)],[.032-.0011*i,.031-.0011*i],12)
        rings.tube([a,a.lerp(b,.04)],.032-.0011*i,12)
    m.finish(f'antenna_pedicel_flagellum_{side}',joint_mat,antenna)
    rings.finish(f'antenna_segment_rings_{side}',amber,antenna)

face_plates=Mesh()
face_plates.sphere((-2.224,0,-.175),(.024,.220,.157),48,32)
face_plates.sphere((-2.208,0,-.370),(.035,.145,.068),40,24)
face_plates.finish('clypeus_and_labrum',chitin,head_lower)
mouth=Mesh()
for side in (-1,1):
    pts=bezier((-2.12,side*.185,-.40),(-2.29,side*.18,-.47),(-2.28,side*.11,-.65),(-2.21,side*.025,-.615),18)
    widths=[.066*(1-i/(len(pts)-1))+.012 for i in range(len(pts))]
    depths=[.024*(1-i/(len(pts)-1))+.005 for i in range(len(pts))]
    mouth.flattened_tube(pts,widths,depths)
mouth.finish('paired_flattened_mandibles',mandible_mat,head_lower)
# Extended mouthparts in the added photographs guide morphology. Keep the
# folded resting posture of the original macro rather than adopting feeding.
proboscis=Mesh()
folded_path=bezier((-2.08,0,-.46),(-1.98,0,-.71),(-1.67,0,-.66),(-1.53,0,-.49),22)
for side in (-1,1):
    sheath=[p+Vector((0,side*.021,0)) for p in folded_path]
    proboscis.flattened_tube(sheath,[.017]*len(sheath),[.009]*len(sheath),10)
proboscis.finish('paired_galeae_folded',mandible_mat,head_lower)
glossa=Mesh()
glossa.tube(folded_path,[.016*(1-i/(len(folded_path)-1))+.007 for i in range(len(folded_path))],10)
glossa.sphere(folded_path[-1],(.017,.014,.022),18,12)
glossa.finish('folded_glossa_and_terminal_labellum',amber,head_lower)
palps=Mesh()
for side in (-1,1):
    palp=[(-2.07,side*.06,-.45),(-2.13,side*.075,-.54),(-1.92,side*.073,-.66),(-1.74,side*.057,-.59)]
    palps.tube(palp,[.021,.022,.014,.004],10)
palps.finish('paired_labial_palps_folded',mandible_mat,head_lower)

print('Building articulated legs...',flush=True)
leg_templates=[
    [(-1.04,.43,-.30),(-1.13,.68,-.46),(-1.49,.99,-.59),(-1.72,1.43,-.98),(-1.97,1.70,-1.17)],
    [(-.52,.49,-.39),(-.42,.74,-.49),(-.18,1.12,-.66),(-.05,1.52,-1.10),(.14,1.77,-1.30)],
    [(-.01,.44,-.34),(.24,.67,-.49),(.85,1.05,-.61),(1.48,1.39,-.92),(1.98,1.65,-1.19)],
]
for side in (-1,1):
    for index, template in enumerate(leg_templates):
        pts=[Vector((x,y*side,z+(.07 if side==1 else 0))) for x,y,z in template]
        g=part(f'leg_{index+1}_{side}','appendage',(.04*(index-1),side*.25,-.12),.3,.8)
        skin,fur,joints=Mesh(),Mesh(),Mesh()
        widths=[.084,.14,.14 if index<2 else .19,.063]
        for i in range(4):
            p,q=pts[i],pts[i+1]
            direction=(q-p).normalized()
            skin.tube([p,p.lerp(q,.20),p.lerp(q,.68),q],[widths[i]*.62,widths[i],widths[i]*.91,widths[i]*.55],14)
            joints.sphere(p,(widths[i]*.68,)*3,16,10)
            ref=direction.cross(Vector((0,0,1))).normalized();ref2=direction.cross(ref).normalized()
            for _ in range(int((270 if i in (1,2) else 100)*DETAIL)):
                t=random.uniform(.06,.95);a=random.uniform(0,math.tau)
                radial=ref*math.cos(a)+ref2*math.sin(a)
                hair(fur,p.lerp(q,t)+radial*widths[i]*.94,radial+direction*.35,random.uniform(.05,.16),radius=.0024,gold=random.random()<.78)
        tarsus=Mesh();rings=Mesh()
        direction=(pts[-1]-pts[-2]).normalized()
        for i in range(5):
            p=pts[-1]+direction*(i*.072)
            q=p+direction*.068
            r=.048-.006*i
            tarsus.tube([p,p.lerp(q,.5),q],[r*.8,r,r*.66],10)
            rings.tube([p,p+direction*.011],r*.86,10)
        claws=Mesh(); tip=pts[-1]+direction*.36
        lateral=direction.cross(Vector((0,0,1))).normalized()
        for s in (-1,1):
            claw_pts=[tip,tip+direction*.07+lateral*s*.06,tip+direction*.075+lateral*s*.073+Vector((0,0,.055))]
            claws.tube(claw_pts,[.015,.011,.002],8)
        claws.sphere(tip+direction*.025,(.027,.025,.032),14,8)
        skin.finish(f'leg_{index+1}_{side}_coxa_femur_tibia',joint_mat,g)
        joints.finish(f'leg_{index+1}_{side}_joints',joint_mat,g)
        fur.finish(f'leg_{index+1}_{side}_setae',hair_mat,g,colored=True)
        tarsus.finish(f'leg_{index+1}_{side}_five_tarsomeres',joint_mat,g)
        rings.finish(f'leg_{index+1}_{side}_rings',amber,g)
        claws.finish(f'leg_{index+1}_{side}_claws_arolium',amber,g)

print('Building four membranous wings and venation...',flush=True)
outline=[(0,0),(.44,.10),(1.15,.20),(2.05,.36),(2.82,.41),(3.08,.25),(3.13,.06),(2.95,-.20),(2.52,-.47),(1.90,-.55),(1.17,-.40),(.48,-.15),(0,-.035)]
# Round the membranous perimeter without changing the measured vein landmarks.
def rounded_outline(points):
    result=[]
    for i in range(len(points)):
        a,b,c,d=[Vector(points[j%len(points)]) for j in (i-1,i,i+1,i+2)]
        for k in range(8):
            t=k/8
            p=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
            result.append(tuple(p))
    return result
outline=rounded_outline(outline)
veins=[
    [(0,0),(.52,.075),(1.17,.17),(2.03,.31),(2.82,.37),(3.07,.25)],
    [(0,-.015),(.46,-.026),(.95,.03),(1.54,.10),(2.13,.18),(2.69,.23),(3.08,.16)],
    [(0,-.03),(.54,-.10),(1.05,-.10),(1.44,-.17),(1.83,-.17),(2.25,-.13),(2.78,-.02),(3.12,.06)],
    [(.22,-.055),(.62,-.18),(1.09,-.28),(1.54,-.33),(1.99,-.35),(2.47,-.26),(2.95,-.13)],
    [(.10,-.03),(.72,-.26),(1.30,-.43),(1.88,-.50),(2.50,-.40)],
    [(.83,.13),(.95,.03),(1.05,-.10),(1.09,-.28)],
    [(1.40,.23),(1.54,.10),(1.44,-.17),(1.54,-.33)],
    [(1.97,.30),(2.13,.18),(2.25,-.13),(1.99,-.35)],
    [(2.63,.37),(2.69,.23),(2.78,-.02),(2.47,-.26)],
]
for side in (-1,1):
    for hind in (False,True):
        root=Vector((-.36 if not hind else -.03,side*.68,.40 if not hind else .26))
        angle=.69 if side==1 else -.34
        if hind: angle+=side*.17
        length=.71 if hind else 1
        width=.67 if hind else 1
        g=part(f'{"hindwing" if hind else "forewing"}_{side}','wing',(.18,side*(.46 if not hind else .30),2.65 if not hind else 2.30),.02,.40)
        def wp(uv):
            u,v=uv[0]*length,uv[1]*width
            return root+Vector((u*math.cos(angle)-v*math.sin(angle),u*math.sin(angle)+v*math.cos(angle),.018*u+.045*v))
        m=Mesh()
        poly=[wp(p) for p in outline]
        indices={tuple(p):m.vertex(p,uv=(outline[i][0]/3.13,(outline[i][1]+.56)/.98)) for i,p in enumerate(poly)}
        for triangle in tessellate_polygon([poly]):
            m.faces.append(tuple(p if isinstance(p, int) else indices[tuple(p)] for p in triangle))
        m.finish(f'wing_membrane_{side}_{hind}',wing_mat,g)
        vein=Mesh()
        for i,path in enumerate(veins):
            vein.tube([wp(p)+Vector((0,0,.003)) for p in path],.0085 if i<2 else .0048,6)
        vein.tube(poly+[poly[0]],.0048,5)
        vein.finish(f'wing_major_veins_{side}_{hind}',vein_mat,g)
        micro=Mesh()
        # Fine folds inside the membrane, bounded by the actual silhouette.
        def inside(u,v):
            yes=False
            j=len(outline)-1
            for i in range(len(outline)):
                xi,yi=outline[i]; xj,yj=outline[j]
                if ((yi>v)!=(yj>v)) and u < (xj-xi)*(v-yi)/(yj-yi)+xi: yes=not yes
                j=i
            return yes
        for _ in range(int(1150*(.5 if MOBILE else 1))):
            u,v=random.uniform(.25,3.02),random.uniform(-.53,.35)
            du,dv=random.uniform(.025,.07),random.uniform(-.028,.028)
            if inside(u,v) and inside(u+du,v+dv):
                micro.tube([wp((u,v)),wp((u+du*.5,v+dv*.4)),wp((u+du,v+dv))],.0007,3)
        micro.finish(f'wing_micro_folds_{side}_{hind}',fine_vein,g)
        if hind:
            hooks=Mesh()
            for i in range(19):
                u=.37+i*.052
                p=wp((u,.10+.075*u))
                hooks.tube([p,p+Vector((0,side*.022,.025)),p+Vector((.006,side*.038,.014))],[.0028,.002,.0005],4)
            hooks.finish(f'hamuli_{side}',vein_mat,g)

print('Building reconstructed organ systems...',flush=True)
random.seed(20261020)  # Keep organ geometry identical between detail levels.
# The crop and the continuous gut are represented in situ until p > .62.
gut=part('system_digestive','digestive',(.2,-1.42,.34),.62,1,True)
m=Mesh()
m.tube([(-2.02,0,-.26),(-1.60,0,-.17),(-.85,0,-.13),(-.15,0,-.14),(.58,0,-.02)],[.028,.031,.035,.037,.048],12)
m.finish('oesophagus',foregut_mat,gut)
# Pear-shaped crop with a narrow anterior entrance. Its degree of distension
# is illustrative, guided by the supplied sagittal models, not measured.
m=Mesh(); rows=[]
for i in range(49):
    t=math.pi*i/48
    x=.87+.41*math.cos(t)
    fullness=.78+.24*math.cos(t)
    rows.append([m.vertex((x,.33*math.sin(t)*fullness*math.cos(j*math.tau/64),-.025+.30*math.sin(t)*fullness*math.sin(j*math.tau/64))) for j in range(65)])
for i in range(48):
    for j in range(64):
        m.faces.append((rows[i][j],rows[i+1][j],rows[i+1][j+1],rows[i][j+1]))
m.finish('crop_honey_stomach',crop_mat,gut)
m=Mesh();m.sphere((1.22,.02,-.02),(.11,.11,.10),28,18);m.finish('proventriculus',gut_mat,gut)
gut_path=bezier((1.24,.01,-.07),(1.58,-.18,-.15),(2.08,-.18,-.28),(2.13,.09,-.27),80)+bezier((2.13,.09,-.27),(2.12,.37,-.28),(1.65,.34,-.33),(1.55,-.06,-.34),64)[1:]
m=Mesh()
m.tube(gut_path,[.155*(1+.21*math.sin(i*math.tau/6.8)) for i in range(len(gut_path))],24)
m.finish('ventriculus_corrugated_midgut',gut_mat,gut)
intestine=bezier((1.55,-.06,-.34),(1.20,-.35,-.40),(2.45,-.44,-.40),(2.35,-.08,-.30),50)
m=Mesh();m.tube(intestine,.05,10);m.sphere((2.40,0,-.27),(.20,.17,.22),32,24);m.tube([(2.48,0,-.34),(2.66,0,-.36)],.027,8);m.finish('ileum_rectum',rectum_mat,gut)
pads=Mesh()
for i in range(6):
    a=i*math.tau/6
    pads.tube([(2.32,.158*math.cos(a),-.27+.16*math.sin(a)),(2.47,.13*math.cos(a),-.27+.15*math.sin(a))],.019,6)
pads.finish('six_rectal_pads',gland_mat,gut)
malp=Mesh()
for i in range(80):
    a=i*math.tau/80
    start=Vector((1.59,-.065,-.34))
    mid=Vector((1.18+.38*math.cos(a),.41*math.sin(a),-.16+.16*math.cos(a)))
    tip=Vector((1.65+.53*math.cos(a*1.7),.44*math.sin(a*1.3),.17+.08*math.sin(a)))
    path=bezier(start,start.lerp(mid,.65),mid,tip,22)
    malp.tube(path,.005,4)
malp.finish('malpighian_tubules_representative_network',excretory_mat,gut)

muscles=part('system_flight_muscles','muscular',(-.2,1.17,.26),.62,1,True)
fibres=Mesh()
for side in (-1,1):
    for row in range(11):
        for col in range(14):
            y=side*(.095+row*.039);z=-.025+col*.044
            if ((abs(y)-.29)/.23)**2+((z-.26)/.32)**2>1: continue
            fibres.tube([(-1.10,y*.86,z-.05),(-.80,y*1.11,z+.05),(-.27,y*1.10,z+.035),(.04,y*.77,z-.09)],[.016,.024,.023,.011],6)
    for i in range(19):
        x=-.98+i*.053;y=side*(.52+.035*math.sin(i))
        fibres.tube([(x,y,-.40),(x+.02,y*.91,-.05),(x-.025,y*.83,.38)],[.025,.030,.021],6)
fibres.finish('longitudinal_and_dorsoventral_flight_fibres',muscle_mat,muscles)

neural=part('system_nervous','neural',(-.16,-.20,-.67),.62,1,True)
m=Mesh()
for side in (-1,1):
    m.sphere((-1.74,side*.15,.22),(.16,.15,.20),32,20)
    m.sphere((-1.75,side*.35,.16),(.10,.18,.16),28,18)
    m.sphere((-1.92,side*.10,.10),(.09,.09,.10),22,14)
    m.tube([(-1.85,side*.11,.11),(-2.05,side*.25,.17)],.013,6)
m.sphere((-1.81,0,-.16),(.10,.12,.085),24,16)
ganglia=[(-.92,-.38,.095),(-.17,-.39,.12),(.61,-.44,.075),(1.07,-.48,.066),(1.49,-.49,.062),(1.89,-.48,.06),(2.24,-.42,.069)]
cord=[(-1.81,0,-.16)]+[(x,0,z) for x,z,r in ganglia]
for side in (-1,1):
    m.tube([(x,side*.019,z) for x,y,z in cord],.012,7)
for x,z,r in ganglia:
    m.sphere((x,0,z),(r*1.3,r,r*.62),22,14)
    for side in (-1,1):
        m.tube([(x,side*.04,z),(x+.055,side*.23,z+.035),(x+.13,side*.41,z+.09)],[.010,.007,.002],5)
m.finish('brain_optic_antennal_lobes_ventral_cord_ganglia',neural_mat,neural)

resp=part('system_tracheal','respiratory',(.04,1.14,-.19),.62,1,True)
m=Mesh(); air_sacs=Mesh()
for side in (-1,1):
    trunk=[(-1.5,side*.31,-.06),(-.99,side*.58,-.06),(-.36,side*.57,-.11),(.40,side*.38,-.07),(.94,side*.56,-.06),(1.51,side*.63,-.06),(2.10,side*.48,-.12),(2.53,side*.20,-.18)]
    m.tube(trunk,[.016,.028,.032,.023,.026,.025,.021,.010],9)
    for i,p in enumerate(trunk[1:-1]):
        p=Vector(p)
        for j in range(5):
            end=p+Vector((random.uniform(-.20,.20),-side*random.uniform(.17,.34),random.uniform(-.19,.26)))
            path=bezier(p,p+Vector((.06,0,.03)),end+Vector((-.04,0,.02)),end,12)
            m.tube(path,[.011*(1-k/len(path))+.001 for k in range(len(path))],5)
            for branch in (-1,1):
                m.tube([path[-5],end+Vector((branch*.06,-side*.06,.05))],[.003,.0009],4)
    air_sacs.sphere((1.07,side*.46,-.05),(.25,.13,.19),32,22)
    air_sacs.sphere((-.40,side*.47,.10),(.20,.10,.23),32,22)
m.finish('tracheal_trunks_and_branches',trachea_mat,resp)
air_sacs.finish('tracheal_air_sac_membranes',air_sac_mat,resp)

heart=part('system_dorsal_vessel','circulatory',(.0,.10,.65),.62,1,True)
m=Mesh()
heart_path=[(-1.73,0,.33),(-1.02,0,.52),(-.36,0,.58),(.35,0,.29),(.66,0,.43),(1.02,0,.52),(1.39,0,.54),(1.77,0,.46),(2.12,0,.33),(2.47,0,.10)]
m.tube(heart_path,[.018,.018,.02,.022,.027,.031,.033,.032,.03,.022],10)
for x in (.71,1.05,1.40,1.75,2.07):
    ry,rz,z=abdomen_profile(x)
    for side in (-1,1):
        m.tube([(x,0,z+rz-.10),(x-.025,side*.10,z+rz-.11)],[.014,.008],7)
m.finish('aorta_heart_five_ostial_regions',heart_mat,heart)

glands=part('system_glands_sting','glandular',(.49,-.72,-.43),.62,1,True)
m=Mesh()
for side in (-1,1):
    for i in range(48):
        t=i/48
        p=(-1.85+.54*t,side*(.26+.065*math.sin(t*20)),.28+.045*math.cos(t*20))
        m.sphere(p,(.027,.03,.028),10,7)
    m.sphere((-1.94,side*.24,-.12),(.10,.08,.13),22,16)
    m.tube([(-1.62,side*.26,.27),(-1.75,side*.12,-.09)],.009,5)
m.sphere((2.25,-.08,-.32),(.19,.11,.09),32,20)
for side in (-1,1):
    m.tube(bezier((2.30,-.08,-.30),(2.12,side*.24,-.25),(1.90,side*.21,-.16),(2.0,side*.25,-.10),24),.011,6)
m.finish('hypopharyngeal_mandibular_venom_glands',gland_mat,glands)
wax=Mesh()
for x in (.98,1.32,1.67,2.0):
    ry,rz,z=abdomen_profile(x)
    for side in (-1,1):
        wax.sphere((x,side*.22,z-rz+.09),(.13,.10,.020),24,14)
wax.finish('four_paired_wax_gland_regions',gland_mat,glands)
scent=Mesh();ry,rz,z=abdomen_profile(2.41)
scent.sphere((2.41,0,z+rz-.045),(.10,.16,.026),28,14)
scent.finish('nasonov_scent_gland_region',gland_mat,glands)
m=Mesh()
for side in (-1,1):
    m.sphere((2.46,side*.08,-.40),(.14,.065,.04),22,14)
    m.tube([(2.48,side*.015,-.39),(2.69,side*.014,-.37),(2.87,side*.008,-.37)],[.013,.009,.0015],8)
m.finish('sting_plates_paired_lancets',amber,glands)

# Editable studio scene. Cameras/lights are not exported into the browser asset.
bpy.ops.object.camera_add(location=(-5.8,-9.3,7.8))
camera=bpy.context.object
camera.name='Reference_study_camera'
camera.rotation_euler=(Vector((-.05,0,.15))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='ORTHO';camera.data.ortho_scale=7.9
bpy.context.scene.camera=camera
for name,loc,power,size in [('Key',(-3,-4,7),1600,5),('Fill',(1,5,4),1300,5),('Rim',(4,-1,5),1700,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    obj=bpy.context.object;obj.name=name;obj.data.energy=power;obj.data.shape='DISK';obj.data.size=size
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.world.color=(.7,.7,.7)
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=32
bpy.context.scene.render.resolution_x=1516
bpy.context.scene.render.resolution_y=1037
bpy.context.scene.render.resolution_percentage=100
if not MOBILE:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'bee-study.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type in ('MESH','EMPTY'): obj.select_set(True)
print('Exporting GLB...',flush=True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'model'/f'bee-study{SUFFIX}.raw.glb'),export_format='GLB',use_selection=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_yup=True)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
stats={'parts':len(PARTS),'meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'seed':20261003,'status':'first procedural reconstruction; not yet anatomically validated','reference':'COLOSS BEEBOOK, Standard methods for Apis mellifera anatomy and dissection, plates 8–12','normalizedUnits':True}
(OUT/f'model-info{SUFFIX}.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(json.dumps(stats),flush=True)
