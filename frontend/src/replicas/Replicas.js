import React, { useState, useEffect, useRef } from 'react';
import { Layout, Table, message, Tag, Popconfirm, Divider, Form, Modal, InputNumber } from 'antd';
import withSidebar from '../common/base';
import { request } from '../helpers';
import { AddReplica } from './EditReplica';

const Content = Layout.Content;

export const EditDelay = Form.create({ name: 'edit_delay' })(
  class extends React.Component {
    render() {
      const { replica, onCancel, onCreate, form } = this.props;
      const { getFieldDecorator } = form;
      const delay = replica ? replica.delay : 0;
      return (
        <Modal
          visible={true}
          title='Edit delay'
          okText='Update'
          onCancel={onCancel}
          onOk={onCreate}
        >
          <Form layout="vertical">
            {
              <Form.Item label="Delay (in minutes)">
                {getFieldDecorator('delay', {
                  initialValue: delay,
                  rules: [{
                    required: true,
                    message: 'Please replica\'s delay!',
                  }],
                })(<InputNumber />)}
              </Form.Item>
            }
          </Form>
        </Modal>
      );
    }
  });

function Replicas() {
  document.title = 'Replicas';

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
    },
    {
      title: 'Type',
      dataIndex: 'type',
    },
    {
      title: 'Replication',
      dataIndex: 'master',
      render: master => {
        const mstr = master ? 'master' : 'replica';
        const color = master ? 'green' : 'geekblue';
        return (
          <Tag color={color} key={mstr}>
            {mstr.toUpperCase()}
          </Tag>
        );
      }
    },
    {
      title: 'Location',
      dataIndex: 'location',
    },
    {
      title: 'Delay',
      dataIndex: 'delay',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      sorter: true,
      render: status => {
        let color;
        if (status === 'ok') {
          color = 'green';
        } else {
          color = 'orange';
        }
        return (
          <Tag color={color} key={status}>
            {status.toUpperCase()}
          </Tag>
        );
      }
    },
    {
      title: 'Files',
      dataIndex: 'files',
    },
    {
      title: 'Action',
      key: 'action',
      render: (text, record) =>
        (!record.master || (record.master && data.length === 1)) ? (
          <span>
            {!record.master &&
              <span>
                {/* eslint-disable-next-line */}
                <a onClick={() => setCurrReplica(record)}>Update delay</a>
                <Divider type="vertical" />
                {/* eslint-disable-next-line */}
                <a onClick={() => setMaster(record)}>Set master</a>
                <Divider type="vertical" />
              </span>
            }
            <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record.id)}>
              {/* eslint-disable-next-line */}
              <a>Delete</a>
            </Popconfirm>
          </span>
        ) : null,
    },
  ];

  let [data, setData] = useState([]);
  let [pagination, setPagination] = useState({});
  let [loading, setLoading] = useState(false);
  let [currReplica, setCurrReplica] = useState(null);
  let editDelayForm = useRef(null);

  useEffect(() => {
    fetch();
    // eslint-disable-next-line
  }, []);

  const handleDelete = (replica) => {
    request(`replicas/${replica}`, { method: 'DELETE' })
      .then(fetch).catch(() => {
        message.error('Deletion failed');
      });
  };

  const updateDelay = () => {
    const { form } = editDelayForm.current.props;
    form.validateFields((err, values) => {
      if (err) {
        return;
      }
      request(`replicas/${currReplica.id}`, { data: values })
        .then(() => {
          form.resetFields();
          setCurrReplica(null);
        })
        .then(fetch).catch(() => {
          message.error('Delay failed to update');
        });
    });
  };

  const setMaster = (replica) => {
    request(`replicas/${replica.id}`, { data: { master: true } })
      .then(fetch).catch(() => message.error('Failed to change master'));
  };

  useEffect(() => {
    const id = setInterval(() => {
      fetch(false);
      setLoading(false);
    }, 2000);
    return () => clearInterval(id);
    // eslint-disable-next-line
  }, []);

  const handleTableChange = (pagination, filters, sorter) => {
    const pager = { ...pagination };
    pager.current = pagination.current;
    setPagination(Object.assign({}, pagination, { current: pagination.current }));
    fetch({
      results: pagination.pageSize,
      page: pagination.current,
      sortField: sorter.field,
      sortOrder: sorter.order,
      ...filters,
    });
  };

  const fetch = (showLoading = true) => {
    if (showLoading) setLoading(true);
    request('replicas').then(data => {
      const pager = Object.assign({}, pagination, { total: data.data.length });
      if (showLoading) setLoading(false);
      setData(data.data);
      setPagination(pager);
    }).catch(e => {
      setLoading(false);
      message.error(e.message);
    });
  };

  const editDelayCancel = () => {
    setCurrReplica(null);
  };
  return (
    <Content style={{
      alignItems: 'center',
      justifyContent: 'center',
      padding: 50
    }}>
      <AddReplica style={{ marginBottom: 10 }} reload={fetch} />
      <Table
        scroll={{ x: 500 }}
        columns={columns}
        rowKey={record => record.id}
        dataSource={data}
        pagination={pagination}
        loading={loading}
        onChange={handleTableChange}
      />
      {
        currReplica !== null &&
        <EditDelay
          wrappedComponentRef={editDelayForm}
          replica={currReplica}
          onCancel={editDelayCancel}
          onCreate={updateDelay}
        ></EditDelay>
      }
    </Content>
  );
}

export default withSidebar(Replicas);
