from db.table import Table
from db.files import Files
from db.file_changes import FileChange
from db.log import Log
from db.patient import Patient
from db.study import Study
from db.series import Series
from db.replica import Replica
from db.replica_files import ReplicaFiles
from db.share_files import SharedFiles
from db.users import Users


Table.register(Log)
Table.register(Patient)
Table.register(Replica)
Table.register(Study)
Table.register(Series)
Table.register(Files)
Table.register(Users)
Table.register(FileChange)
Table.register(ReplicaFiles)
Table.register(SharedFiles)
