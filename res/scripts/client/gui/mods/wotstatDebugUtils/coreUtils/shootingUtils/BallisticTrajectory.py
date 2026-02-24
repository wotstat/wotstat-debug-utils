import math

from Math import Vector3
from projectile_trajectory import computeProjectileTrajectory
from realm import CURRENT_REALM

from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from typing import Tuple, Optional

IS_LESTA = CURRENT_REALM == 'RU'
SHELL_TRAJECTORY_EPSILON = 0.02

class BallisticTrajectory(object):
  
  def __init__(self, startPoint, startVelocity, acceleration):
    # type: (Vector3, Vector3, Vector3) -> None

    self.startPoint = startPoint
    self.startVelocity = startVelocity
    self.acceleration = acceleration

  @property
  def gravity(self):
    return self.acceleration.y

  def getPoint(self, time):
    return self.startPoint + self.startVelocity * time + self.acceleration * (0.5 * time * time)
  
  def getVelocity(self, time):
    return self.startVelocity + self.acceleration * time
  
  def getTrajectoryPoints(self, timeFrom, timeTo, epsilon=SHELL_TRAJECTORY_EPSILON):
    startPos = self.getPoint(timeFrom)
    startVel = self.getVelocity(timeFrom)

    acceleration = self.acceleration if IS_LESTA else self.gravity

    points = computeProjectileTrajectory(startPos, startVel, acceleration, timeTo - timeFrom, epsilon)
    points.insert(0, startPos)

    return points
  
  def getTrajectoryDistance(self, time, timeFrom=0):
    if time == timeFrom:
      return 0.0

    tStart = min(timeFrom, time)
    tEnd = max(timeFrom, time)

    A = self.acceleration
    V = self.startVelocity

    qa = A.lengthSquared
    qb = 2.0 * V.dot(A)
    qc = V.lengthSquared

    eps = 1e-12
    if qa <= eps:
      return math.sqrt(max(qc, 0.0)) * (tEnd - tStart)

    sqrtQa = math.sqrt(qa)
    k = 4.0 * qa * qc - qb * qb

    def _speedIntegralPrimitive(t):
      speedSq = qa * t * t + qb * t + qc
      if speedSq < 0.0 and speedSq > -1e-9:
        speedSq = 0.0
      speed = math.sqrt(max(speedSq, 0.0))

      linearTerm = (2.0 * qa * t + qb) * speed / (4.0 * qa)
      if abs(k) <= eps:
        return linearTerm

      logArg = 2.0 * sqrtQa * speed + 2.0 * qa * t + qb
      if logArg < eps:
        logArg = eps

      logTerm = (k / (8.0 * qa * sqrtQa)) * math.log(logArg)
      return linearTerm + logTerm

    return _speedIntegralPrimitive(tEnd) - _speedIntegralPrimitive(tStart)

  def getNearestPoint(self, point, timeFrom=None, timeTo=None):
    # type: (Vector3, Optional[float], Optional[float]) -> Tuple[Vector3, float, float]
    """Find the nearest point on the trajectory to the given coordinate.
    Minimizes |P(t) - point|^2 analytically by solving the cubic derivative.
    Negative time is allowed. Returns (nearestPoint, time).
    """
    S = self.startPoint
    V = self.startVelocity
    A = self.acceleration
    D = S - point # type: Vector3

    # P(t) = S + V*t + 0.5*A*t^2
    # f(t) = |P(t) - point|^2 = |D + V*t + 0.5*A*t^2|^2
    # f'(t)/2 = (D + V*t + 0.5*A*t^2) . (V + A*t) = 0
    # Expanding: 0.5*|A|^2*t^3 + 1.5*(A.V)*t^2 + (|V|^2 + D.A)*t + D.V = 0
    a3 = 0.5 * A.lengthSquared
    a2 = 1.5 * A.dot(V)
    a1 = V.lengthSquared + D.dot(A)
    a0 = D.dot(V)

    candidates = _solveCubic(a3, a2, a1, a0)

    if timeFrom is not None:
      candidates.append(timeFrom)
    if timeTo is not None:
      candidates.append(timeTo)

    if timeFrom is not None or timeTo is not None:
      tMin = timeFrom if timeFrom is not None else float('-inf')
      tMax = timeTo if timeTo is not None else float('inf')
      candidates = [t for t in candidates if tMin - 1e-9 <= t <= tMax + 1e-9]

    if not candidates:
      if timeFrom is not None:
        candidates.append(timeFrom)
      if timeTo is not None:
        candidates.append(timeTo)
      if not candidates:
        candidates.append(0.0)

    bestTime = None
    bestDistSq = float('inf')
    bestPoint = None

    for t in candidates:
      p = S + V * t + A * (0.5 * t * t) # type: Vector3
      distSq = p.distSqrTo(point)
      if distSq < bestDistSq:
        bestDistSq = distSq
        bestTime = t
        bestPoint = p

    return bestPoint, bestTime, math.sqrt(bestDistSq)

  def getTimeAtDistance(self, distance, timeFrom=0, epsilon=1e-6):
    # type: (float, float, float) -> Optional[float]
    """Find the time at which the arc length from timeFrom equals the given distance.
    Uses binary search on the monotonically increasing arc length function.
    Returns None if distance is negative.
    """
    if distance < 0:
      return None
    if distance == 0:
      return timeFrom

    speed = self.getVelocity(timeFrom).length
    if speed < 1e-12:
      if self.acceleration.lengthSquared < 1e-24:
        return None
      dt = 1.0
    else:
      dt = distance / speed

    tHigh = timeFrom + dt
    while self.getTrajectoryDistance(tHigh, timeFrom) < distance:
      dt *= 2.0
      tHigh = timeFrom + dt

    tLow = timeFrom

    for _ in range(100):
      tMid = (tLow + tHigh) * 0.5
      if tHigh - tLow < epsilon:
        break
      if self.getTrajectoryDistance(tMid, timeFrom) < distance:
        tLow = tMid
      else:
        tHigh = tMid

    return (tLow + tHigh) * 0.5

def _cbrt(x):
  if x >= 0:
    return x ** (1.0 / 3.0)
  return -((-x) ** (1.0 / 3.0))

def _solveQuadratic(a, b, c):
  EPS = 1e-12
  if abs(a) < EPS:
    if abs(b) < EPS:
      return []
    return [-c / b]
  disc = b * b - 4.0 * a * c
  if disc < 0:
    return []
  if disc < EPS:
    return [-b / (2.0 * a)]
  sq = math.sqrt(disc)
  return [(-b + sq) / (2.0 * a), (-b - sq) / (2.0 * a)]

def _solveCubic(a, b, c, d):
  """Solve at^3 + bt^2 + ct + d = 0. Returns list of real roots."""
  EPS = 1e-12
  if abs(a) < EPS:
    return _solveQuadratic(b, c, d)

  p = b / a
  q = c / a
  r = d / a

  alpha = q - p * p / 3.0
  beta = r - p * q / 3.0 + 2.0 * p * p * p / 27.0

  offset = -p / 3.0
  disc = beta * beta / 4.0 + alpha * alpha * alpha / 27.0

  if disc > EPS:
    sqrtDisc = math.sqrt(disc)
    u = _cbrt(-beta / 2.0 + sqrtDisc)
    v = _cbrt(-beta / 2.0 - sqrtDisc)
    return [u + v + offset]
  elif disc < -EPS:
    rr = math.sqrt((-alpha / 3.0) ** 3)
    cosArg = max(-1.0, min(1.0, -beta / (2.0 * rr)))
    theta = math.acos(cosArg) / 3.0
    t = 2.0 * math.sqrt(-alpha / 3.0)
    return [
      t * math.cos(theta) + offset,
      t * math.cos(theta - 2.0 * math.pi / 3.0) + offset,
      t * math.cos(theta + 2.0 * math.pi / 3.0) + offset
    ]
  else:
    if abs(beta) < EPS:
      return [offset]
    u = _cbrt(-beta / 2.0)
    return [2.0 * u + offset, -u + offset]
