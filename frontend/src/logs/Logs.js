import React, { useState, useEffect } from 'react';
import { Layout, Table, message } from 'antd';
import withSidebar from '../common/base';
import { request } from '../helpers';

const Content = Layout.Content;

const columns = [
  {
    title: 'Time',
    dataIndex: 'created',
    width: '20%',
    render: data => new Date(data * 1000).toUTCString(),
  },
  {
    title: 'Log',
    dataIndex: 'log',
    render: data => {
      const lines = data.split('\n');
      return lines.slice(-2);
    }
  }
];

function Logs() {
  document.title = 'Logs';

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
    request('logs').then(data => {
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
    <Content style={{
      alignItems: 'center',
      justifyContent: 'center',
      padding: 50
    }}>
      <Table
        columns={columns}
        rowKey={record => record.id}
        expandedRowRender={record => <p style={{ margin: 0 }}>{record.log}</p>}
        dataSource={data}
        pagination={pagination}
        loading={loading}
        onChange={handleTableChange}
      />
    </Content>
  );
}

export default withSidebar(Logs);
