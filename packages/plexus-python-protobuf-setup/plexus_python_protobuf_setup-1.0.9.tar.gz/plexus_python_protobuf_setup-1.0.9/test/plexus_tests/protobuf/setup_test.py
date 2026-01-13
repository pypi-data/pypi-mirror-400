import os
import tempfile
import unittest

import plexus.protobuf.setup
from plexus_tests import resources_directory


class TestSetup(unittest.TestCase):

    def test_compile_protos(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            proto_dirs = [os.path.join(resources_directory, "unittest", "setup", "protos")]
            include_dirs = [os.path.join(resources_directory, "unittest", "setup", "protos")]

            plexus.protobuf.setup.compile_protos(temp_dir,
                                                 proto_dirs,
                                                 include_dirs,
                                                 package_root_dir=os.path.join(temp_dir, "dummy"),
                                                 descriptor_path=os.path.join(temp_dir, "descriptor.proto"),
                                                 with_grpc=True)

            self.assertTrue(os.path.exists(os.path.join(temp_dir, "descriptor.proto")))
            self.assertFalse(os.path.exists(os.path.join(temp_dir, "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "person_pb2.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "person_pb2.pyi")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "person_pb2_grpc.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "company_pb2.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "company_pb2.pyi")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "company_pb2_grpc.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "family_pb2.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "family_pb2.pyi")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "family_pb2_grpc.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "__init__.py")))

    def test_compile_protos__without_grpc(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            proto_dirs = [os.path.join(resources_directory, "unittest", "setup", "protos")]
            include_dirs = [os.path.join(resources_directory, "unittest", "setup", "protos")]

            plexus.protobuf.setup.compile_protos(temp_dir, proto_dirs, include_dirs, with_grpc=False)

            self.assertFalse(os.path.exists(os.path.join(temp_dir, "descriptor.proto")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "person_pb2.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "person_pb2.pyi")))
            self.assertFalse(os.path.exists(os.path.join(temp_dir, "dummy", "person_pb2_grpc.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "company_pb2.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "company_pb2.pyi")))
            self.assertFalse(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "company_pb2_grpc.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "family_pb2.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "family_pb2.pyi")))
            self.assertFalse(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "family_pb2_grpc.py")))
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "dummy", "relationship", "__init__.py")))
