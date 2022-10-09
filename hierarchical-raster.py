import copy
import pygame as pg
import math

pg.init()

scalefactor = 4
resbits = 7
videosize = (1 << resbits, 1 << resbits)
videobuf = pg.Surface(videosize)
vram = {'img': pg.image.load('texture.png'), 'pixels': None}

# screen init
window = pg.display.set_mode((videosize[0]*scalefactor, videosize[1]*scalefactor), pg.HWSURFACE)

pg.display.set_caption("blitter")
black = (0, 0, 0)
white = (255, 255, 255)
clock = pg.time.Clock()



# 3d point class
class Point:

  # constructor function, pos and tex must be defined at a 3-tuple
  def __init__(self, name=None, pos=None, tex=None):

    if name is None:
      self.name = "pt"
    else:
      self.name = name

    # point position attribute (x, y, z)
    if pos is None:
      self.pos = [0]*3
    else:
      self.pos = pos

    # point texture attribute (u, v, t)
    if tex is None:
      self.tex = [0]*3
    else:
      self.tex = tex


# primitive class used to draw polygons
class Primitive:

  # organized as 4 directions (update axis, sign)
  nx = [(0, 1), (1, 1), (1, -1), (0, -1)]

  # edge function computation (cross-product of 3 points)
  def edge(self, va, vb, vc):
    e = [(va.pos[1] - vb.pos[1]), (vb.pos[0] - va.pos[0]), (va.pos[0] * vb.pos[1]) - (va.pos[1] * vb.pos[0])]
    return [e[0], e[1], e[2], e[0]*vc.pos[0] + e[1]*vc.pos[1] + e[2]]

  # initiate Primitive instance
  def __init__(self, cfg, v0, v1, v2):

    self.cfg = cfg
    self.pt = Point()
    self.vt = [v0, v1, v2]
    self.w = [0]*4 #[copy.copy(w0), copy.copy(w1), copy.copy(w2), copy.copy(sz)]
    self.eq = [0]*3 #[copy.copy(w0[3]), copy.copy(w1[3]), copy.copy(w2[3])]
    self.dv = 0 #65535 // sz[3]

    self.update()

    #self.w = [w0, w1, w2, sz]
    #self.eq = [copy.copy(w0[3]), copy.copy(w1[3]), copy.copy(w2[3])]

    print("primitive equations, area:{0}".format(self.w[3][3]))

  # simplification of area calculation
  #  self.sz = self.w0[2] + self.w1[2] + self.w2[2]
  # another possible simplification of area and w0 calculation
  # self.sz = self.w2[0]*self.v2[0] + self.w2[1]*self.v2[1] + self.w2[2]
  # self.w0 = self.area - (self.w1 + self.w2)

  def update(self):

    # todo: clip primitive to screen area, and decide on best point location

    # compute edge equations
    w0 = self.edge(self.vt[1], self.vt[2], self.pt)
    w1 = self.edge(self.vt[2], self.vt[0], self.pt)
    w2 = self.edge(self.vt[0], self.vt[1], self.pt)
    sz = self.edge(self.vt[0], self.vt[1], self.vt[2])

    #self.w = [w0, w1, w2, sz]
    self.w = [copy.copy(w0), copy.copy(w1), copy.copy(w2), copy.copy(sz)]
    self.eq = [copy.copy(w0[3]), copy.copy(w1[3]), copy.copy(w2[3])]
    self.dv = sz[3]#((1 << 15)-1) // sz[3]

    # adjust pixels to centers (by accum half a step)
    #for i in (0, 1, 2):
    #  self.eq[i] += (self.w[i][0] + self.w[i][1]) >> 1
      #print("w[{0}] : {1}, eq[{0}] : {2}".format(i, self.w[i], self.eq[i]))

  # compute direction of current position
  def eq_dir(self, shift):
    return (((self.pt.pos[1] >> shift) & 0x1) << 1) | ((self.pt.pos[0] >> shift) & 0x1)

  # increment equations by step amount
  def eq_step(self, dir, shift):

    # grab which step to use based on direction (axis, direction)
    step = self.nx[dir]

    # increment current pixel position
    self.pt.pos[step[0]] += step[1] * (1 << shift)
    #videobuf.set_at((self.pt.pos[0], self.pt.pos[1]), 0x0000ff)

    #print("step: {0}, {1}x".format(step, 1<<shift))

    # interpolate each edge equation by the increment amount
    for i in (0, 1, 2):

      # sign * equation step amount shifted by current tile size
      inc_step = step[1] * (self.w[i][step[0]] << shift)

      # sub-tile offset (typically not required)
      #inc_offset = self.w[i][step[0]] * offset

      # todo: compute u,v equations here as well!

      # add together to generate new equations
      self.eq[i] += inc_step# + inc_offset

  # dumb inside triangle pixel logic
  def inside(self, eq, ea, eb):
    if eq > 0:
      return True
    if eq < 0:
      return False
    if ea > 0:
      return True
    if ea < 0:
      return False
    if ea == 0 and eb < 0:
      return False
    return True
    # if eq >= 0:
    #   return True
    # return False

  # run through tile and rasterize it
  def raster(self, sh=2):

    xh = 1 << sh
    ix = self.pt.pos[0]
    iy = self.pt.pos[1]
    ar = self.dv
    dv = 65535 // ar
    #print("ar: {:}, r-1: {:}".format(ar, dv))

    # compute equations
    dx = [self.w[0][0], self.w[1][0], self.w[2][0]]
    dy = [self.w[0][1], self.w[1][1], self.w[2][1]]
    dw = [self.w[0][2], self.w[1][2], self.w[2][2]]

    bb = 8

    ux = [dx[0]*dv, dx[1]*dv, dx[2]*dv]
    uy = [dy[0]*dv, dy[1]*dv, dy[2]*dv]
    uw = [dw[0]*dv, dw[1]*dv, dw[2]*dv]

    vx = ux
    vy = uy
    vw = uw


    w = [0]*3
    u = [0]*3
    v = [0]*3
    for i in range(0, 3):
      w[i] = ix * dx[i] + iy * dy[i] + dw[i]
      u[i] = ix * ux[i] + iy * uy[i] + uw[i]
      b[i] = ix * vx[i] + iy * vy[i] + vw[i]

    x = 0
    y = 0
    m = 1

    while (True):

      # render if inside
      if self.inside(w[0], 0, 0) and self.inside(w[1], 0, 0) and self.inside(w[2], 0, 0):
        #c0 = int((w[0] << 8) // ar)
        #c1 = int((w[1] << 8) // ar)
        #c2 = int((w[2] << 8) // ar)

        u0 = u[0] >> bb
        u1 = u[1] >> bb
        u2 = u[2] >> bb
        v0 = v[0] >> bb
        v1 = v[1] >> bb
        v2 = v[2] >> bb

        if u0 < 0:
          u0 = 0
        if u1 < 0:
          u1 = 0
        if u2 < 0:
          u2 = 0
        if v0 < 0:
          v0 = 0
        if v1 < 0:
          v1 = 0
        if v2 < 0:
          v2 = 0

        #print("test: {:} {:} {:} {:} {:} {:}".format(c0, c1, c2, d0, d1, d2))
        #color = ((c0 & 0xff) << 16) | ((c1 & 0xff) << 8) | (c2 & 0xff)
        #color = ((d0 & 0xff) << 16) | ((d1 & 0xff) << 8) | (d2 & 0xff)
        color = vram["img"].get_at((uk, vk))
        #color = ((b0 & 0xff) << 16) | ((c1 & 0xff) << 8) | (c2 & 0xff)
        videobuf.set_at((ix+x, iy+y), color)

      # positive moving x
      if m == 1:

        # if next x is sh, go down one and begin going left
        if x + 1 >= xh:

          m = -1
          y += 1
          for i in range(0, 3):
            w[i] += dy[i]
            b[i] += by[i]

        # increment x by 1
        else:

          x += 1
          for i in range(0, 3):
            w[i] += dx[i]
            b[i] += bx[i]

      # negative moving x
      else:

        # if current x is 0, go down one and begin going right
        if x == 0:

          m = 1
          y += 1
          for i in range(0, 3):
            w[i] += dy[i]
            b[i] += by[i]

        else:

          x += m
          for i in range(0, 3):
            w[i] += dx[i] * m
            b[i] += bx[i] * m

      if y >= xh:
        return

  # render primitive via hierarchical raster algorithm
  def render(self):

    init_sh = resbits-1

    sh = init_sh
    done = False

    # re-initiate point
    self.pt = Point()

    # while not at final shift level and direction
    while not done:

      # initiate condition flags as True
      drawmsk = [1] * 4
      skipblk = [1] * 3

      # iterate through each sub-block
      # all of this will happen in parallel {
      for i in (0, 1, 3, 2):

        # compute w0-3 for each sample point
        for j in (0, 1, 2):

          # assign skip block flag based on if equation j is negative
          skipblk[j] &= self.eq[j] < 0

          # assign draw mask flag based on if equation j is renderable
          test = self.inside(self.eq[j], self.w[j][1], self.w[j][2])
          drawmsk[i] &= test

        #videobuf.set_at((self.pt.pos[0], self.pt.pos[1]), [0xff0000, 0x00ff00][drawmsk[i]])
        window.blit(pg.transform.scale(videobuf, window.get_rect().size), (0, 0))
        pg.display.update()

        # iterate to next sub-block
        self.eq_step(i, sh)
      # } end of parallel block

      # in hardware, this is the state decision tree based on parallel results {
      # if at lowest shift value (4x4)
      if sh == 2:

        self.raster(sh)
        skip = True

      # if all drawmsk is true, do not subdivide because it can draw the entire block
      elif drawmsk[0] and drawmsk[1] and drawmsk[2] and drawmsk[3]:

        self.raster(sh)
        skip = True

      # if at least one draw mask is enabled, do not skip
      elif drawmsk[0] or drawmsk[1] or drawmsk[2] or drawmsk[3]:

        skip = False

      # otherwise, if a skipblk is true, do not subdivide, skip the entire block
      elif skipblk[0] or skipblk[1] or skipblk[2]:

        skip = True

      # in all other cases, further subdivide
      else:
        skip = False

      # if decision is to skip
      if skip:

        # compute current direction
        dir = self.eq_dir(sh)

        # jump to next tile of current subdivision
        self.eq_step(dir, sh)

        # if at final step direction of current subdivision
        while dir == 2:

          # if at initial shift level, render is complete
          if sh == init_sh:

            done = True
            dir = 0

          # otherwise, increment shift and jump to next upward state
          else:

            sh += 1

            # compute current direction
            dir = self.eq_dir(sh)

            # jump to next tile of current subdivision
            self.eq_step(dir, sh)

      # if we didn't skip, we must subdivide further
      else:

        sh -= 1
      # } end of parallel decision tree

# clear screen and render initial output
videobuf.fill(black)
window.blit(pg.transform.scale(videobuf, window.get_rect().size), (0, 0))
pg.display.update()
quitGame = False

#v0 = Point([4, 8, 0])
#v1 = Point([12, 0, 0])
#v2 = Point([14, 14, 0])

v0 = Point("V0",[10, 10, 0])
v1 = Point("V1",[127, 20, 0])
v2 = Point("V2",[0, 127, 0])
v3 = Point("V3",[120, 110, 0])

TRI_NUM = 2

tri = [0]*TRI_NUM
tri[0] = Primitive(0, v0, v1, v2)
tri[1] = Primitive(0, v3, v2, v1)

mousepos = []
mouseclk = []
pt_sel = None #tri.vt[0]

font = pg.font.SysFont(None, 15)
#pg.event.post(pg.MOUSEBUTTONUP)

videobuf.fill(black)

for k in range(0, TRI_NUM):
  tri[k].update()

  for i in tri[k].vt:
    videobuf.set_at((i.pos[0], i.pos[1]), 0xffffff)
    if i.pos[0] >= 0 and (i.pos[1]+6) >= 0:
      text = font.render(i.name, False, 0xffffff, None)
      textRect = text.get_rect()
      textRect.center = (i.pos[0], i.pos[1]+6)
      videobuf.blit(text, textRect)
  tri[k].render()

render_complete = True

# main loop
while not quitGame:

  mousepos = pg.mouse.get_pos()
  mx = (mousepos[0] // scalefactor)
  my = (mousepos[1] // scalefactor)

  for event in pg.event.get():
    if event.type == pg.QUIT:
      quitGame = True

    elif event.type == pg.MOUSEBUTTONDOWN:
      mouseclk = pg.mouse.get_pressed(num_buttons=3)

      for k in range(0, TRI_NUM):
        for vt in tri[k].vt:
          if mx == vt.pos[0] and my == vt.pos[1]:
            if mouseclk[0]:
              pt_sel = vt
              print("selected pt: ", pt_sel)
              render_complete = False

    elif event.type == pg.MOUSEBUTTONUP:
      mousepos = [0,0]
      mouseclk = [0,0,0]
      pt_sel = None

  if pt_sel is not None:
    pt_sel.pos[0] = mx
    pt_sel.pos[1] = my

    videobuf.fill(black)

    for k in range(0, TRI_NUM):
      tri[k].pt.pos = [0,0,0]
      for i in tri[k].vt:
        videobuf.set_at((i.pos[0], i.pos[1]), 0xffffff)

  elif not render_complete:

    videobuf.fill(black)
    for k in range(0, TRI_NUM):
      tri[k].update()
      tri[k].render()

      for i in tri[k].vt:
        videobuf.set_at((i.pos[0], i.pos[1]), 0xffffff)
        if i.pos[0] >= 0 and (i.pos[1]+6) >= 0:
          text = font.render(i.name, False, 0xffffff, None)
          textRect = text.get_rect()
          textRect.center = (i.pos[0], i.pos[1]+6)
          videobuf.blit(text, textRect)
    render_complete = True

  #window.blit(pg.transform.scale(videobuf, window.get_rect().size), (0, 0))

  #if textRect:
  #textRect = text.get_rect()

  window.blit(pg.transform.scale(videobuf, window.get_rect().size), (0, 0))
  pg.display.update()

  clock.tick(60)

pg.quit()
