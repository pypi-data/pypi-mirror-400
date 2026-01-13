import pyarrow as pa
from loguru import logger

def serialize_to_pyarrow_ipc(attribute) -> bytes:
    """
    Serialize a single Telekinesis datatype into Arrow IPC bytes.

    Args:
        attribute: Telekinesis datatype object.

    Returns:
        bytes: The serialized PyArrow IPC bytes.
    """
    
	# Validate if attribute object has the attribute
    if not hasattr(attribute, "to_pyarrow"):
        raise TypeError(f"{type(attribute).__name__} does not implement to_pyarrow()")

    pyarrow_dict = attribute.to_pyarrow()
    if not isinstance(pyarrow_dict, dict):
        raise TypeError("to_pyarrow() must return dict[str, pa.Array]")

    fields = []
    arrays = []

    for field_name, array in pyarrow_dict.items():

        fields.append(
            pa.field(
                field_name,
                array.type,
                nullable=True,
                metadata={
                    b"telekinesis_datatype": attribute.telekinesis_datatype.encode("utf8")
                },
            )
        )
        arrays.append(array)

    schema = pa.schema(fields)
    record_batch = pa.RecordBatch.from_arrays(arrays, schema=schema)

	# Arrow level compression
    options = pa.ipc.IpcWriteOptions(
    compression="lz4",
	)

    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, schema, options=options) as writer:
        writer.write_batch(record_batch)
        
    logger.info(f"Serialized {type(attribute).__name__} to Arrow IPC")
        
    return sink.getvalue().to_pybytes()


def deserialize_from_pyarrow_ipc(ipc_bytes: bytes):
    """
    Deserialize a single Arrow IPC stream into one Telekinesis datatype.
    
    Args:
        ipc_bytes (bytes): The serialized PyArrow IPC bytes.

    Returns:
        Telekinesis datatype object.
    """
    
    buffer = pa.BufferReader(ipc_bytes)
    reader = pa.ipc.open_stream(buffer)

    grouped_fields = {}
    datatype_str = None

    for batch in reader:
        for i, field in enumerate(batch.schema):
            metadata = field.metadata
            if not metadata or b"telekinesis_datatype" not in metadata:
                raise ValueError(
                    f"Missing telekinesis_datatype metadata for field '{field.name}'"
                )

            field_datatype = metadata[b"telekinesis_datatype"].decode("utf8")
            if datatype_str is None:
                datatype_str = field_datatype
            elif datatype_str != field_datatype:
                raise ValueError(
                    "Multiple telekinesis_datatype values found in one IPC stream"
                )

            grouped_fields[field.name] = batch.column(i)

    if datatype_str is None:
        raise ValueError("No telekinesis_datatype found in IPC stream")

    module_name, class_name = datatype_str.rsplit(".", 1)
    module = __import__(module_name, fromlist=[class_name])
    cls = getattr(module, class_name)
    
    logger.info(f"Deserialied {class_name} from Arrow IPC")

    if not hasattr(cls, "from_pyarrow"):
        raise NotImplementedError(
            f"{class_name} does not implement from_pyarrow()"
        )

    return cls.from_pyarrow(grouped_fields)


