import numpy as np
from numpy.linalg import inv, LinAlgError


class KalmanFilter:
    def __init__(self, A: np.array, B: np.array, H: np.array, Q: np.array, R: np.array):
        '''
        :param A: Matrix that represents how the state evolves from t-1 to t, without control or noise
        :param B: Matrix that represents how the control changes the state from t-1 to t
        :param C: Matrix that describes how to map the state xt to an observation zt
        :param Q: Covariance matrix that represents the uncertainty gained from time propagation
        :param R: Covariance matrix that represents the uncertainty gained from observation/measurement
        :param dt: standard time interval
        '''
        self.A: np.array = A
        self.B: np.array = B
        self.H: np.array = H
        self.Q: np.array = Q
        self.R: np.array = R

        # Kalman filter state:
        self.last_mean: np.array = None
        self.last_sigma: np.array = None

        self.dimension = A.shape[0]

    def predict(self, ut, last_mean=None, last_sigma=None):
        # boilerplate for checking last_mean
        if last_mean is None:
            if self.last_mean is None:
                raise ValueError("Must inform last_mean on the first run")
            else:
                last_mean = self.last_mean  # use the saved state

        # boilerplate for checking last_sigma
        if last_sigma is None:
            if self.last_sigma is None:
                raise ValueError("Must inform last_sigma on the first run")
            else:
                last_sigma = self.last_sigma  # use the saved state

        # actual calculation
        predicted_mean = self.A @  last_mean + self.B @ ut
        predicted_sigma = self.A @ last_sigma @ self.A.transpose() + self.Q
        # print(f"predicted_mean:\n {predicted_mean}\n predicted_sigma:\n {predicted_sigma}")

        return predicted_mean, predicted_sigma

    def update(self, zt, predicted_mean, predicted_sigma):
        # calculation
        den = inv(self.H @ predicted_sigma @ self.H.transpose() + self.R)
        Kt = predicted_sigma @ self.H.transpose() @ den
        updated_mean = predicted_mean + Kt @ (zt - self.H @ predicted_mean)
        updated_sigma = (np.identity(self.dimension) - Kt @ self.H) @ predicted_sigma

        # saving state for next run
        self.last_mean = updated_mean
        self.last_sigma = updated_sigma
        # print(f"Kt:\n {Kt}\nupdated_mean:\n {updated_mean}\n updated_sigma:\n {updated_sigma}")

        return updated_mean, updated_sigma

    def step(self, ut, zt, last_mean=None, last_sigma=None):
        predicted_mean, predicted_sigma = self.predict(ut, last_mean, last_sigma)
        return self.update(zt, predicted_mean, predicted_sigma)


class CarSystemKF:
    def __init__(self, manager, dt: float = 1):
        self.mng = manager
        self.started = False
        mea = self.mng.sensor.measurement_noise

        # Kalman Filter parameters:
        A = np.array(
            [[1, dt, 0.5*dt*dt, 0, 0, 0],
             [0, 1, dt, 0, 0, 0],
             [0, 0, 1, 0, 0, 0],
             [0, 0, 0, 1, dt, 0.5*dt*dt],
             [0, 0, 0, 0, 1, dt],
             [0, 0, 0, 0, 0, 1]]
        )
        B = np.array([[0], [0], [1], [0], [0], [1]])  # control effects acceleration, basically
        H = np.identity(n=6)
        # this covariance matrix come from experimentations with covariance_lab.py
        P = np.array(
                            [[1, 1, 1, 0, 0, 0],
                             [1, 2, 3, 0, 0, 0],
                             [1, 3, 6, 0, 0, 0],
                             [0, 0, 0, 1, 1, 1],
                             [0, 0, 0, 1, 2, 3],
                             [0, 0, 0, 1, 3, 6]]
        )
        R = P * mea * dt
        Q = P * dt * 2
        # Q = np.zeros((6, 6))
        self.kf = KalmanFilter(A, B, H, Q, R)

        # initialize sigma
        if not self.started:
            # initial_sigma = np.identity(6)
            initial_sigma = P
            self.kf.last_sigma = initial_sigma

    def get_state_from_measure(self, measure):
        assert len(measure) == 3

        measured_pos, measured_vel, measured_acc = measure

        assert len(measured_pos) == len(measured_vel) == len(measured_acc) == 2

        mean = np.array(
            [[measured_pos[0]],
             [measured_vel[0]],
             [measured_acc[0]],
             [measured_pos[1]],
             [measured_vel[1]],
             [measured_acc[1]]]
        )
        return mean

    def update(self, measure):
        mean = self.get_state_from_measure(measure)

        if not self.started:
            self.kf.last_mean = mean
            self.started = True

        ut = np.zeros((1, 1))
        result = self.kf.step(ut, mean)

        return result

