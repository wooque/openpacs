import React, { useState, useRef, useEffect } from 'react';
import { Table, Input, Form, message } from 'antd';
import { request } from '../helpers';

const EditableContext = React.createContext();

const EditableRow = ({ form, index, ...props }) => (
  <EditableContext.Provider value={form}>
    <tr {...props} />
  </EditableContext.Provider>
);

const EditableFormRow = Form.create()(EditableRow);

const editableFields = [];

const EditableCell = (props) => {
  let [editing, setEditing] = useState(false);
  let form = useRef();
  let input = useRef();

  const toggleEdit = () => {
    if (!editableFields.includes(props.record.key)) return;
    const e = !editing;
    setEditing(e);
  };

  useEffect(() => {
    if (editing) {
      input.current.focus();
    }
  }, [editing]);

  const save = e => {
    const { record, handleSave } = props;
    form.current.validateFields((error, values) => {
      if (error && error[e.currentTarget.id]) {
        return;
      }
      toggleEdit();
      if (record.value !== values.value) {
        handleSave({ ...record, ...values });
      }
    });
  };

  const renderCell = form_ => {
    form.current = form_;
    const { children, dataIndex, record, title } = props;
    return editing ? (
      <Form.Item style={{ margin: 0 }}>
        {form.current.getFieldDecorator(dataIndex, {
          rules: [
            {
              required: true,
              message: `${title} is required.`,
            },
          ],
          initialValue: record[dataIndex],
        })(<Input ref={input} onPressEnter={save} onBlur={save} />)}
      </Form.Item>
    ) : (
      <div
        className="editable-cell-value-wrap"
        style={{ paddingRight: 24 }}
        onClick={toggleEdit}
      >
        {children}
      </div>
    );
  };

  const {
    editable,
    dataIndex,
    title,
    record,
    index,
    handleSave,
    children,
    ...restProps
  } = props;
  return (
    <td {...restProps}>
      {editable ? (
        <EditableContext.Consumer>{renderCell}</EditableContext.Consumer>
      ) : (
        children
      )}
    </td>
  );
};

const EditableTable = props => {
  let columns = [
    {
      title: 'key',
      dataIndex: 'key',
      width: '20%',
    },
    {
      title: 'value',
      dataIndex: 'value',
      editable: true,
      width: '70%',
    },
  ];
  let [dataSource, setDataSource] = useState(props.file.meta);
  let [search, setSearch] = useState('');

  const metaToDatasource = () => {
    let ds = Object.entries(props.file.meta || {}).map(e => {
      return { 'key': e[0], 'value': e[1] };
    });
    return ds.sort((a, b) => a.key.localeCompare(b.key));
  };

  useEffect(() => {
    const ds = metaToDatasource();
    setDataSource(ds);
    setSearch('');
    // eslint-disable-next-line
  }, [props.file]);

  useEffect(() => {
    let ds = metaToDatasource();
    ds = ds.filter(d => d.key.toLowerCase().startsWith(search.toLowerCase()));
    setDataSource(ds);
    // eslint-disable-next-line
  }, [search]);

  const onSearchChange = e => {
    setSearch(e.target.value);
  };

  const handleSave = row => {
    const newData = [...dataSource];
    const index = newData.findIndex(item => row.key === item.key);
    const item = newData[index];
    request(`files/${props.file.id}`, { data: { tag: row } }).then(() => {
      newData.splice(index, 1, {
        ...item,
        ...row,
      });
      setDataSource(newData);
    }).catch(() => message.error('Failed to save'));
  };

  const components = {
    body: {
      row: EditableFormRow,
      cell: EditableCell,
    },
  };
  const cols = columns.map(col => {
    if (!col.editable) {
      return col;
    }
    return {
      ...col,
      onCell: record => ({
        record,
        editable: col.editable,
        dataIndex: col.dataIndex,
        title: col.title,
        handleSave: handleSave,
      }),
    };
  });
  return (
    <div style={props.style}>
      {/* <Button onClick={handleAdd} type="primary" style={{ marginBottom: 16 }}>
        Add a row
      </Button> */}
      <Input placeholder="Search..." onChange={onSearchChange} value={search}></Input>
      <Table
        scroll={{ x: 500 }}
        components={components}
        rowClassName={() => 'editable-row'}
        bordered
        dataSource={dataSource}
        columns={cols}
        loading={props.loading}
        pagination={props.pagination}
        rowKey={props.rowKey}
      />
    </div>
  );
};

export default EditableTable;