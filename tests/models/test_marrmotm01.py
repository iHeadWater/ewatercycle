from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest
import xarray as xr
from numpy.testing import assert_almost_equal
from scipy.io import loadmat
from xarray.testing import assert_allclose

from ewatercycle import CFG
from ewatercycle.forcing import load_foreign
from ewatercycle.models import MarrmotM01
from ewatercycle.models.marrmot import Solver


@pytest.fixture
def mocked_config(tmp_path):
    CFG['output_dir'] = tmp_path
    CFG['container_engine'] = 'docker'


class TestWithDefaultsAndExampleData:
    @pytest.fixture
    def forcing_file(self, sample_marrmot_forcing_file):
        return sample_marrmot_forcing_file

    @pytest.fixture
    def generate_forcing(self, forcing_file):
        forcing = load_foreign('marrmot',
                               directory=str(Path(forcing_file).parent),
                               start_time='1989-01-01T00:00:00Z',
                               end_time='1992-12-31T00:00:00Z',
                               forcing_info={
                                   'forcing_file': str(Path(forcing_file).name)
                               })
        return forcing

    @pytest.fixture
    def model(self, generate_forcing, mocked_config):
        m = MarrmotM01(version="2020.11", forcing=generate_forcing)
        yield m
        if m.bmi:
            # Clean up container
            del m.bmi

    @pytest.fixture
    def model_with_setup(self, model: MarrmotM01):
        cfg_file, cfg_dir = model.setup()
        return model, cfg_file, cfg_dir

    def test_parameters(self, model, forcing_file):

        expected = [
            ('maximum_soil_moisture_storage', 10.0),
            ('initial_soil_moisture_storage', 5.0),
            ('solver', Solver()),
            ('start time', '1989-01-01T00:00:00Z'),
            ('end time', '1992-12-31T00:00:00Z'),
            ('forcing_file', forcing_file)
        ]
        assert model.parameters == expected

    def test_setup(self, model_with_setup, forcing_file):
        model, cfg_file, cfg_dir = model_with_setup

        actual = loadmat(str(cfg_file))
        expected_forcing = loadmat(forcing_file)

        assert cfg_file.name == 'marrmot-m01_config.mat'
        assert model.bmi
        assert actual['model_name'] == "m_01_collie1_1p_1s"
        assert_almost_equal(actual['time_start'], expected_forcing['time_start'])
        assert_almost_equal(actual['time_end'], expected_forcing['time_end'])
        # TODO compare forcings
        # assert_almost_equal(actual['forcing'], expected_forcing['forcing'])
        # TODO assert solver
        # assert actual['solver'] == asdict(Solver())

    def test_parameters_after_setup(self, model_with_setup, forcing_file):
        model = model_with_setup[0]
        expected = [
            ('maximum_soil_moisture_storage', 10.0),
            ('initial_soil_moisture_storage', 5.0),
            ('solver', Solver()),
            ('start time', '1989-01-01T00:00:00Z'),
            ('end time', '1992-12-31T00:00:00Z'),
            ('forcing_file', forcing_file)
        ]
        assert model.parameters == expected

    def test_get_value_as_xarray(self, model_with_setup):
        model, cfg_file, cfg_dir = model_with_setup
        model.initialize(str(cfg_file))
        model.update()

        actual = model.get_value_as_xarray('flux_out_Q')

        expected = xr.DataArray(
            data=[[11.91879913]],
            coords={
                "longitude": [87.49],
                "latitude": [35.29],
                "time": datetime(1989, 1, 2, tzinfo=timezone.utc)
            },
            dims=["latitude", "longitude"],
            name='flux_out_Q',
            attrs={"units": 'mm day'},
        )
        assert_allclose(actual, expected)

    def test_setup_with_own_work_dir(self, tmp_path, mocked_config, model: MarrmotM01):
        cfg_file, cfg_dir = model.setup(
            work_dir=tmp_path
        )
        assert cfg_dir == tmp_path


class TestWithCustomSetupAndExampleData:
    @pytest.fixture
    def forcing_file(self, sample_marrmot_forcing_file):
        return sample_marrmot_forcing_file

    @pytest.fixture
    def generate_forcing(self, forcing_file):
        forcing = load_foreign('marrmot',
                                directory=str(Path(forcing_file).parent),
                                start_time='1989-01-01T00:00:00Z',
                                end_time='1992-12-31T00:00:00Z',
                                forcing_info={
                                    'forcing_file': str(Path(forcing_file).name)
                                })
        return forcing

    @pytest.fixture
    def model(self, generate_forcing, mocked_config):
        m = MarrmotM01(version="2020.11", forcing=generate_forcing)
        yield m
        if m.bmi:
            # Clean up container
            del m.bmi

    @pytest.fixture
    def model_with_setup(self, model: MarrmotM01):
        cfg_file, cfg_dir = model.setup(
            maximum_soil_moisture_storage=1234,
            initial_soil_moisture_storage=4321,
            start_time='1990-01-01T00:00:00Z',
            end_time='1991-12-31T00:00:00Z',
        )
        return model, cfg_file, cfg_dir

    def test_setup(self, model_with_setup):
        model, cfg_file, cfg_dir = model_with_setup

        actual = loadmat(str(cfg_file))
        assert cfg_file.name == 'marrmot-m01_config.mat'
        assert model.bmi
        assert actual['model_name'] == "m_01_collie1_1p_1s"
        assert actual['parameters'] == [[1234]]
        assert actual['store_ini'] == [[4321]]
        assert_almost_equal(actual['time_start'], [[1990,   1,   1,    0,    0,    0]])
        assert_almost_equal(actual['time_end'], [[1991,   12,   31,    0,    0,    0]])


class TestWithDatesOutsideRangeSetupAndExampleData:
    @pytest.fixture
    def forcing_file(self, sample_marrmot_forcing_file):
        return sample_marrmot_forcing_file

    @pytest.fixture
    def generate_forcing(self, forcing_file):
        forcing = load_foreign('marrmot',
                                directory=str(Path(forcing_file).parent),
                                start_time='1989-01-01T00:00:00Z',
                                end_time='1992-12-31T00:00:00Z',
                                forcing_info={
                                    'forcing_file': str(Path(forcing_file).name)
                                })
        return forcing

    @pytest.fixture
    def model(self, generate_forcing, mocked_config):
        m = MarrmotM01(version="2020.11", forcing=generate_forcing)
        yield m
        if m.bmi:
            # Clean up container
            del m.bmi

    def test_setup_with_earlystart(self, model: MarrmotM01):
        with pytest.raises(ValueError) as excinfo:
            model.setup(
                start_time='1980-01-01T00:00:00Z',
            )
        assert 'start_time outside forcing time range' in str(excinfo.value)

    def test_setup_with_lateend(self, model: MarrmotM01):
        with pytest.raises(ValueError) as excinfo:
            model.setup(
                end_time='2000-01-01T00:00:00Z',
            )
        assert 'end_time outside forcing time range' in str(excinfo.value)