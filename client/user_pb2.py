# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: user.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'user.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nuser.proto\x12\x04user\"[\n\x13RegisterUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x11\n\tlow_value\x18\x03 \x01(\x02\x12\x12\n\nhigh_value\x18\x04 \x01(\x02\"\'\n\x14RegisterUserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"Y\n\x11UpdateUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x0e\n\x06ticker\x18\x02 \x01(\t\x12\x11\n\tlow_value\x18\x03 \x01(\x02\x12\x12\n\nhigh_value\x18\x04 \x01(\x02\"%\n\x12UpdateUserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"J\n\x12UpdateValueRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x11\n\tlow_value\x18\x02 \x01(\x02\x12\x12\n\nhigh_value\x18\x03 \x01(\x02\"&\n\x13UpdateValueResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"\"\n\x11\x44\x65leteUserRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\"%\n\x12\x44\x65leteUserResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x07\n\x05\x45mpty\"\x1d\n\x0c\x45mailRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\"3\n\x13\x41verageStockRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\r\n\x05\x63ount\x18\x02 \x01(\x05\"4\n\x12StockValueResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02\"\x1f\n\x0f\x41llDataResponse\x12\x0c\n\x04\x64\x61ta\x18\x01 \x03(\t\"-\n\x17\x44\x65leteDataByTimeRequest\x12\x12\n\nstart_time\x18\x01 \x01(\x03\"+\n\x18\x44\x65leteDataByTimeResponse\x12\x0f\n\x07message\x18\x01 \x01(\t2\xaf\x04\n\x0bUserService\x12\x45\n\x0cRegisterUser\x12\x19.user.RegisterUserRequest\x1a\x1a.user.RegisterUserResponse\x12?\n\nUpdateUser\x12\x17.user.UpdateUserRequest\x1a\x18.user.UpdateUserResponse\x12\x42\n\x0bUpdateValue\x12\x18.user.UpdateValueRequest\x1a\x19.user.UpdateValueResponse\x12?\n\nDeleteUser\x12\x17.user.DeleteUserRequest\x1a\x18.user.DeleteUserResponse\x12\x30\n\nGetAllData\x12\x0b.user.Empty\x1a\x15.user.AllDataResponse\x12\x41\n\x11GetLastStockValue\x12\x12.user.EmailRequest\x1a\x18.user.StockValueResponse\x12K\n\x14GetAverageStockValue\x12\x19.user.AverageStockRequest\x1a\x18.user.StockValueResponse\x12Q\n\x10\x44\x65leteDataByTime\x12\x1d.user.DeleteDataByTimeRequest\x1a\x1e.user.DeleteDataByTimeResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'user_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_REGISTERUSERREQUEST']._serialized_start=20
  _globals['_REGISTERUSERREQUEST']._serialized_end=111
  _globals['_REGISTERUSERRESPONSE']._serialized_start=113
  _globals['_REGISTERUSERRESPONSE']._serialized_end=152
  _globals['_UPDATEUSERREQUEST']._serialized_start=154
  _globals['_UPDATEUSERREQUEST']._serialized_end=243
  _globals['_UPDATEUSERRESPONSE']._serialized_start=245
  _globals['_UPDATEUSERRESPONSE']._serialized_end=282
  _globals['_UPDATEVALUEREQUEST']._serialized_start=284
  _globals['_UPDATEVALUEREQUEST']._serialized_end=358
  _globals['_UPDATEVALUERESPONSE']._serialized_start=360
  _globals['_UPDATEVALUERESPONSE']._serialized_end=398
  _globals['_DELETEUSERREQUEST']._serialized_start=400
  _globals['_DELETEUSERREQUEST']._serialized_end=434
  _globals['_DELETEUSERRESPONSE']._serialized_start=436
  _globals['_DELETEUSERRESPONSE']._serialized_end=473
  _globals['_EMPTY']._serialized_start=475
  _globals['_EMPTY']._serialized_end=482
  _globals['_EMAILREQUEST']._serialized_start=484
  _globals['_EMAILREQUEST']._serialized_end=513
  _globals['_AVERAGESTOCKREQUEST']._serialized_start=515
  _globals['_AVERAGESTOCKREQUEST']._serialized_end=566
  _globals['_STOCKVALUERESPONSE']._serialized_start=568
  _globals['_STOCKVALUERESPONSE']._serialized_end=620
  _globals['_ALLDATARESPONSE']._serialized_start=622
  _globals['_ALLDATARESPONSE']._serialized_end=653
  _globals['_DELETEDATABYTIMEREQUEST']._serialized_start=655
  _globals['_DELETEDATABYTIMEREQUEST']._serialized_end=700
  _globals['_DELETEDATABYTIMERESPONSE']._serialized_start=702
  _globals['_DELETEDATABYTIMERESPONSE']._serialized_end=745
  _globals['_USERSERVICE']._serialized_start=748
  _globals['_USERSERVICE']._serialized_end=1307
# @@protoc_insertion_point(module_scope)
