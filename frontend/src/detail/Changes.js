import React, { useState, useEffect } from 'react';
import { Table, message, Tag } from 'antd';
import { request } from '../helpers';

const columns = [
  {
    title: 'time',
    dataIndex: 'created',
    width: '30%',
    render: data => new Date(data * 1000).toUTCString(),
  },
  {
    title: 'username',
    dataIndex: 'username',
    width: '10%',
  },
  {
    title: 'change',
    dataIndex: 'type',
    width: '70%',
    render: data => {
      return (
        <Tag color='orange'>{data}</Tag>
      );
    }
  },
];

function Changes(props) {

  let [data, setData] = useState([]);
  let [pagination, setPagination] = useState({});
  let [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch();
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

  const fetch = () => {
    setLoading(true);
    request(`files/${props.file.id}/changes`).then(data => {
      const pager = Object.assign({}, pagination, { total: data.data.length });
      setLoading(false);
      setData(data.data);
      setPagination(pager);
    }).catch(e => {
      setLoading(false);
      message.error(e.message);
    });
  };

  return (
    <Table
      scroll={{ x: 500 }}
      columns={columns}
      rowKey={record => record.id}
      dataSource={data}
      pagination={pagination}
      loading={loading}
      onChange={handleTableChange}
    />
  );
}

export default Changes;
