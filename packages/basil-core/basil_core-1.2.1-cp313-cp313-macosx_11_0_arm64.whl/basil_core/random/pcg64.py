#!/usr/env/bin python3
"""Utilities for random number generation"""
######## Imports ########
from os import path
import warnings
#### Standard Library ####
#### Third Party ####
import numpy as np
#### Homemade ####

class PCG64GeneratorState(object):
    """An API for the PCG64 bit generator state"""
    def __init__(
        self,
        state_value,
        inc_value,
        has_uint32=False,
        uinteger=False,
    ):
        # Store values
        self.state_value=state_value
        self.inc_value=inc_value
        self.has_uint32=has_uint32
        self.uinteger=uinteger

    @property
    def bit_generator(self):
        return "PCG64"

    @property
    def state_value_dict(self):
        return {
            "state" : self.state_value,
            "inc"   : self.inc_value,
        }

    @property
    def export(self):
        return {
            "bit_generator" : self.bit_generator,
            "state" : self.state_value_dict,
            "has_uint32" : self.has_uint32,
            "uinteger" : self.uinteger,
        }

    def to_xdata(self,fname,group):
        """Save to hdf5 using Vera's xev-data package"""
        try:
            from xdata import Database
        except:
            raise ImportError("Try `pip install xev-data`")
        # Open a pointer object to the database
        db_ptr = Database(fname)
        # Create the group if necessary
        if not db_ptr.exists(group):
            db_ptr.create_group(group)
        # Store attributes
        db_ptr.attr_set(group,"state_value",str(self.state_value))
        db_ptr.attr_set(group,"inc_value",str(self.inc_value))
        db_ptr.attr_set(group,"has_uint32",int(self.has_uint32))
        db_ptr.attr_set(group,"uinteger",int(self.uinteger))
        db_ptr.attr_set(group,"bit_generator",self.bit_generator)
        db_ptr.attr_set(group,"numpy_version",np.__version__)
    
    def numpy_generator(self):
        """Return a numpy generator"""
        # Create generator
        gen = np.random.Generator(np.random.PCG64())
        # Apply state
        gen.bit_generator.state = self.export
        return gen

    @staticmethod
    def from_xdata(fname,group):
        """Load a state from hdf5 using Vera's xev-data package"""
        try:
            from xdata import Database
        except:
            raise ImportError("Try `pip install xev-data`")
        # Check if the file exists
        if not path.isfile(fname):
            raise IOError(f"No such file: {fname}!")
        # Open a pointer object to the database
        db_ptr = Database(fname)
        # Check if the group exists
        if not db_ptr.exists(group):
            raise IOError(f"No such group {group} in {fname}!")
        # Initialize temporary dictionary
        attributes = {}
        for key in [
            "state_value", 
            "inc_value", 
            "has_uint32", 
            "uinteger", 
            "bit_generator",
        ]:
            # Check if attribute exists
            if not db_ptr.attr_exists(group,key):
                raise ValueError(
                    f"No such attribute {key} in {group} for {fname}")
            # Load key
            attributes[key] = db_ptr.attr_value(group,key)
        return PCG64GeneratorState(
            int(attributes["state_value"]),
            int(attributes["inc_value"]),
            has_uint32 = int(attributes["has_uint32"]),
            uinteger = int(attributes["uinteger"]),
        )

    @staticmethod
    def from_Generator(numpy_gen):
        """Create a new state object from a NumPy Generator"""
        # Export the state
        _state = numpy_gen.state
        # Load attributes
        state_value = _state["state"]["state"]
        inc_value = _state["state"]["inc"]
        has_uint32 = _state["has_uint32"]
        uinteger = _state["uinteger"]
        return PCG64GeneratorState(
            state_value,
            inc_value,
            has_uint32 = has_uint32,
            uinteger = uinteger,
        )

class PCG64GeneratorAPI(object):
    """An API for PCG64 number generators using NumPy's Generator objects"""
    def __init__(self,seed=None):
        """Create a new instance of a PCG64 Generator object"""
        # Get numpy generator
        self.generator = np.random.Generator(np.random.PCG64(seed))

    # Define how to save this thing
    def to_xdata(self,fname,group):
        from xdata import Database
        # Save to hdf5
        self.state.to_xdata(fname,group)
        # Open a pointer object to the database
        db_ptr = Database(fname)
        # set the seed sequence entropy
        db_ptr.attr_set(group,"seed_entropy",
            str(self.generator.bit_generator.seed_seq.entropy))

    # Load from xdata
    @staticmethod
    def from_xdata(fname,group):
        from xdata import Database
        # Extract state
        state_obj = PCG64GeneratorState.from_xdata(fname,group)
        # Open a pointer object to the database
        db_ptr = Database(fname)
        # Get the seed sequence entropy
        entropy = int(db_ptr.attr_value(group,"seed_entropy"))
        # Initialize the seed sequence
        seq = np.random.SeedSequence(entropy=entropy)
        # Instantiate object
        api_obj = PCG64GeneratorAPI(seed=seq)
        # Input state
        api_obj.generator.bit_generator.state = state_obj.export
        return api_obj

    # State object as property
    @property
    def state(self):
        return PCG64GeneratorState.from_Generator(self.generator.bit_generator)

    @state.setter
    def state(self, value):
        if isinstance(value, dict):
            self.generator.bit_generator.state = value
        elif isinstance(value, PCG64GeneratorState):
            self.generator.bit_generator.state = value.export
        else:
            raise ValueError(f"Unknown datatype passed to state setter:"
                f"value {value} has type {type(value)}")
    
    # getter
    def __getattr__(self, key):
        if hasattr(self.generator, key):
            return getattr(self.generator, key)
        else:
            return AttributeError(f"self.generator has no attribute {key}")

    # Spawn new objects
    def spawn(self,n=1):
        """Spawn new generator objects"""
        # First case: one new generator
        if n == 1:
            # Initialize the new generator
            child = PCG64GeneratorAPI()
            # Call the random number generator api
            child_bit_gen = self.generator.spawn(1)[0].bit_generator
            # spawn new bit generator
            # Assign the child's state object
            child.state = PCG64GeneratorState.from_Generator(child_bit_gen)
            return child
        elif n > 1:
            # Initialize list of children
            children = []
            # spawn child bit generators
            child_bit_gen = self.generator.spawn(n)
            # Loop
            for i in range(n):
                # New object
                child = PCG64GeneratorAPI()
                # Assign state
                child.state = PCG64GeneratorState.from_Generator(
                    child_bit_gen[i].bit_generator,
                )
                # Append children
                children.append(child)
            return children

    # Copy
    def copy(self):
        """Return a copy of this generator"""
        # Define the new seed sequence
        seq = np.random.SeedSequence(
            entropy=self.generator.bit_generator.seed_seq.entropy,
        )
        # Define a new generator
        gen = PCG64GeneratorAPI(seed=seq)
        # Update its state
        gen.state = self.state
        # Return generator
        return gen

def seed_parser(seed):
    """Parse seed and guarantee that you return a random number generator

    Parameters
    ----------
    seed : unknown
        Something for random number generation

    Returns
    -------
    rng : PCG64GeneratorAPI
        A better RNG object
    """
    # Case 1: PCG64GeneratorAPI; noop
    if isinstance(seed, PCG64GeneratorAPI):
        return seed
    # Case 2: PCG64GeneratorState
    elif isinstance(seed, PCG64GeneratorState):
        rng = PCG64GeneratorAPI()
        rng.state = seed.export
        return rng
    # Case 3: np.random.RandomState object
    elif isinstance(seed, np.random.RandomState):
        warnings.warn(
            f"{seed} is not reccomended for Monte Carlo; "
            f"this will be deprecated use a np.random.Generator object in the future.",
            DeprecationWarning
        )
        return seed
    # Case 4: np.random.Generator; noop
    elif isinstance(seed, np.random.Generator):
        return seed
    # Case 5: np.random.SeedSequence
    elif isinstance(seed, np.random.SeedSequence):
        return np.random.Generator(seed)
    elif seed is None:
        rng = PCG64GeneratorAPI()
        return rng
    # Case 7: something else
    else:
        warnings.warn(
            f"{seed} was passed as random number generator uninitialized; "
            "if you do this more than once your samples will be correlated."
        )
        return PCG64GeneratorAPI(seed)

######## Tests ########
def test_state():
    # Generate a state from a seed
    bit_gen = np.random.PCG64(42)
    # Capture the state
    bit_gen_state = PCG64GeneratorState.from_Generator(bit_gen)
    # Print it
    # Try saving it
    bit_gen_state.to_xdata("tmp.hdf5","rng")
    # Try loading it
    bit_gen_state_load = PCG64GeneratorState.from_xdata("tmp.hdf5","rng")
    # Test random number efficacy
    gen_first = bit_gen_state.numpy_generator()
    gen_load = bit_gen_state_load.numpy_generator()
    gen_copy = bit_gen_state_load.numpy_generator()
    uniform_first = gen_first.uniform(low=0.,high=1.,size=10)
    uniform_load = gen_load.uniform(low=0.,high=1.,size=10)
    uniform_copy = gen_copy.uniform(low=0.,high=1.,size=10)
    assert np.all(uniform_first == uniform_load)
    assert np.all(uniform_first == uniform_copy)
    return

def test_api():
    from xdata import Database
    # Initialize a new generator object
    gen = PCG64GeneratorAPI(seed=87)
    # Define filename
    fname = "tmp.hdf5"
    # Open a database
    db_ptr = Database(fname,group="example")
    # Loop
    for i in range(8):
        # Identify tag
        tag = "random-set-%03d"%i
        # Save the generator
        gen.to_xdata(fname,tag)
        # Generate some data
        x = gen.uniform(size=10)
        # Save the data
        db_ptr.dset_set(tag,x)
    # Instantiate a new generator
    gen2 = PCG64GeneratorAPI()
    # Loop
    for i in range(8):
        # Identify tag
        tag = f"random-set-{i:03d}"
        # Load the generator
        gen2 = PCG64GeneratorAPI.from_xdata(fname,tag)
        # load data
        x = db_ptr.dset_value(tag)
        # Generate data
        x2 = gen2.uniform(size=10)
        # Check equivalence
        assert np.allclose(x, x2)
    # Spawn child
    child1 = gen.spawn()
    child2 = gen2.spawn()
    # Draw samples
    x = child1.uniform(size=10)
    x2 = child2.uniform(size=10)
    # check equivalence
    assert np.allclose(x,x2)
    # Check copy
    child3 = child1.copy()
    x = child1.uniform(size=10)
    x3 = child3.uniform(size=10)
    # Check equivalence
    assert np.allclose(x,x3)


######## Main ########
def main():
    test_state()
    test_api()

######## Execution ########
if __name__ == "__main__":
    main()
