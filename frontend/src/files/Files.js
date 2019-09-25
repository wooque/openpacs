import React, { useState, useEffect, useRef } from 'react';
import { Link, withRouter } from 'react-router-dom';
import Highlighter from 'react-highlight-words';
import { Layout, Table, Input, message, Button, Icon, Row, Col } from 'antd';
import withSidebar from '../common/base';
import { request, open } from '../helpers';
import { AdminFiles } from './AdminFiles';
import AdvancedSearch from './AdvancedSearch';
import { PAGINATION } from '../config';
import './Files.css';

const Content = Layout.Content;
const Search = Input.Search;

function encodeUrl(obj) {
  return '?' + encodeURIComponent(JSON.stringify(obj));
}

function decodeUrl(url) {
  if (!url.length) return {};
  return JSON.parse(decodeURIComponent(url.slice(1)));
}

const initialAdvancedFields = [
  ['Patient ID', ''],
  ['Patient\'s Name', ''],
  ['Patient\'s Age', ''],
  ['Patient\'s Gender', ''],
  ['Study ID', ''],
  ['Study Description', ''],
  ['Series Number', ''],
  ['Series Modality', ''],
  ['Series Description', ''],
  ['Referring Physician\'s Name', ''],
  ['Performing Physician\'s Name', ''],
  ['SOP Class UID', ''],
];

function Files(props) {
  document.title = 'Search';

  let [data, setData] = useState([]);
  let [pagination, setPagination] = useState({ pageSize: PAGINATION.limit });
  let [loading, setLoading] = useState(false);
  let [showUpload, setShowUpload] = useState(false);
  let [showAdvanced, setShowAdvanced] = useState(false);
  let searchInput = useRef(null);
  let [globSearchCurrent, setGlobSearchCurrent] = useState('');
  let [globSearch, setGlobSearch] = useState('');
  let [searchText, setSearchText] = useState('');
  let [advancedFields, setAdvancedFields] = useState(initialAdvancedFields.map(e => [...e]));
  let [selected, setSelected] = useState([]);

  const handleTableChange = (pagination, filters, sorter) => {
    const pager = { ...pagination };
    pager.current = pagination.current;
    setPagination(Object.assign({}, pagination, { current: pagination.current }));
    let s = {
      results: pagination.pageSize,
      page: pagination.current,
      sortField: sorter.field,
      sortOrder: sorter.order,
      ...filters,
    };
    if (globSearch) {
      s.query = globSearch;
    }
    if (advancedFields) {
      let so = {};
      for (let f of advancedFields) {
        if (!f[0].length || !f[1].length) continue;
        so[f[0]] = [f[1]];
      }
      s = Object.assign(s, so);
    }
    props.history.push(encodeUrl(s));
  };

  useEffect(() => {
    fetch();
    // eslint-disable-next-line
  }, [window.location.search]);

  useEffect(() => {
    setPagination(Object.assign({}, pagination, { pageSize: PAGINATION.limit }));
    fetch();
    // eslint-disable-next-line
  }, [PAGINATION.limit]);

  const fetch = () => {
    setLoading(true);
    const searchObj = decodeUrl(window.location.search);
    if (searchObj.query) {
      setGlobSearch(searchObj.query);
      setSearchText('');
    } else {
      let set = false;
      for (let k in searchObj) {
        if (Array.isArray(searchObj[k])) {
          setSearchText(searchObj[k][0]);
          setGlobSearch('');
          set = true;
        }
      }
      if (!set) {
        setGlobSearch('');
        setSearchText('');
      }
    }
    request('files', { data: searchObj }).then(data => {
      setLoading(false);
      setData(data.data);
      setPagination(Object.assign({}, pagination, { total: data.total }));
    }).catch(e => {
      setLoading(false);
      message.error(e.message);
    });
  };

  const downloadFiles = () => {
    if (!selected || !selected.length) return;

    open('files/download.zip?ids=' + selected.join(','))
      .catch(() => {
        message.error('Fail to download');
      });
  };

  const downloadData = () => {
    if (!selected || !selected.length) return;

    open('files/download.csv?ids=' + selected.join(','))
      .catch(() => {
        message.error('Fail to download');
      });
  };

  const handleSearchChange = (e) => {
    setPagination(Object.assign({}, pagination, { current: 1 }));
    setGlobSearchCurrent(e.target.value);
  };

  const handleSearch = (value) => {
    setAdvancedFields(initialAdvancedFields.map(e => [...e]));
    setSearchText('');
    setGlobSearch(value);
    if (value) {
      props.history.push(encodeUrl({ query: value }));
    } else {
      props.history.push('');
    }
  };

  const getColumnSearchProps = (dataIndex, options = {}) => ({
    filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
      <div style={{ padding: 8 }}>
        <Input
          ref={node => {
            searchInput.current = node;
          }}
          placeholder={`Search ${dataIndex}`}
          value={selectedKeys[0]}
          onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
          onPressEnter={() => handleColumnSearch(selectedKeys, confirm)}
          style={{ width: 188, marginBottom: 8, display: 'block' }}
        />
        <Button
          type="primary"
          onClick={() => handleColumnSearch(selectedKeys, confirm)}
          icon="search"
          size="small"
          style={{ width: 90, marginRight: 8 }}
        >
          Search
        </Button>
        <Button onClick={() => handleReset(clearFilters)} size="small" style={{ width: 90 }}>
          Reset
        </Button>
      </div>
    ),
    filterIcon: filtered => (
      <Icon type="search" style={{ color: filtered ? '#1890ff' : undefined }} />
    ),
    onFilterDropdownVisibleChange: visible => {
      if (visible) {
        setTimeout(() => searchInput.current.select());
      }
    },
    render: (text, record) => {
      if (options.render) {
        return options.render(text, record);
      }
      let searchWords = [searchText];
      if (globSearch) {
        searchWords.push(globSearch);
      }
      return (
        <Highlighter
          highlightStyle={{ backgroundColor: '#ffc069', padding: 0 }}
          searchWords={searchWords}
          autoEscape
          textToHighlight={text ? text.toString() : ''}
        />
      );
    },
  });

  const handleColumnSearch = (selectedKeys, confirm) => {
    confirm();
    setPagination(Object.assign({}, pagination, { current: 1 }));
    setGlobSearchCurrent('');
    setGlobSearch('');
    setSearchText(selectedKeys[0]);
  };

  const handleReset = clearFilters => {
    clearFilters();
    setSearchText('');
  };

  const onAdvancedSearchChangeLabel = (i, e) => {
    advancedFields[i][0] = e.target.value;
    setAdvancedFields([...advancedFields]);
  };

  const onAdvancedSearchChange = (i, e) => {
    advancedFields[i][1] = e.target.value;
    setAdvancedFields([...advancedFields]);
  };

  const onAdvancedSearchAdd = () => {
    setAdvancedFields([...advancedFields, ['', '']]);
  };

  const onAdvancedSearchRemove = i => {
    advancedFields.splice(i, 1);
    setAdvancedFields([...advancedFields]);
  };

  const onAdvancedSearch = () => {
    setSearchText('');
    setGlobSearchCurrent('');
    setGlobSearch('');
    setShowAdvanced(false);
    let so = {};
    for (let f of advancedFields) {
      if (!f[0].length || !f[1].length) continue;
      so[f[0]] = [f[1]];
    }
    props.history.push(encodeUrl(so));
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      render: (text, record) => <Link to={'/files/' + record.id}>{text}</Link>,
    },
    {
      title: 'Patient ID',
      dataIndex: 'Patient ID',
      ...getColumnSearchProps('Patient ID', {
        render: (text, record) => <Link to={'/patients/' + record.patient_db_id}>{text}</Link>
      }),
    },
    {
      title: 'Patient Name',
      dataIndex: 'Patient\'s Name',
      ...getColumnSearchProps('Patient\'s Name'),
    },
    {
      title: 'Study ID',
      dataIndex: 'Study ID',
      ...getColumnSearchProps('Study ID'),
    },
    {
      title: 'Study Description',
      dataIndex: 'Study Description',
      ...getColumnSearchProps('Study Description'),
    },
    {
      title: 'Series Number',
      dataIndex: 'Series Number',
      ...getColumnSearchProps('Series Number'),
    },
    {
      title: 'Series Description',
      dataIndex: 'Series Description',
      ...getColumnSearchProps('Series Description'),
    },
  ];

  const rowSelection = {
    onChange: (selectedRowKeys, selectedRows) => {
      setSelected(selectedRowKeys);
    },
    getCheckboxProps: record => ({
      disabled: false,
      name: record.name,
    }),
  };

  return (
    <Content className="files">
      <Row>
        <Col span={16}>
          <Search
            placeholder="input search text"
            enterButton="Search"
            size="large"
            onSearch={handleSearch}
            style={{
              marginBottom: 10
            }}
            value={globSearchCurrent}
            onChange={handleSearchChange}
          />
        </Col>
        <Col span={8}>
          <Button
            size='large' type='primary'
            onClick={() => setShowAdvanced(true)}
          >
            Advanced
          </Button>
        </Col>
      </Row>
      <Button style={{ marginBottom: '10px' }} type="primary"
        onClick={() => setShowUpload(true)}>
        Upload
      </Button>
      <Button style={{ marginBottom: '10px', marginLeft: '5px' }} type="primary"
        onClick={() => downloadFiles()}>
        Download files
      </Button>
      <Button style={{ marginBottom: '10px', marginLeft: '5px' }} type="primary"
        onClick={() => downloadData()}>
        Download data
      </Button>
      <AdvancedSearch
        visible={showAdvanced}
        onClose={() => setShowAdvanced(false)}
        onSearch={onAdvancedSearch}
        fields={advancedFields}
        onChangeLabel={onAdvancedSearchChangeLabel}
        onChange={onAdvancedSearchChange}
        onAdd={onAdvancedSearchAdd}
        onRemove={onAdvancedSearchRemove}
        fixed={initialAdvancedFields.length}
      />
      <AdminFiles
        visible={showUpload}
        onClose={() => {
          fetch();
          setShowUpload(false);
        }}>
      </AdminFiles>
      <Table
        className='filesTable'
        scroll={{ x: 500 }}
        columns={columns}
        rowKey={record => record.id}
        dataSource={data}
        rowSelection={rowSelection}
        pagination={pagination}
        loading={loading}
        onChange={handleTableChange}
      />
    </Content>
  );
}

export default withRouter(withSidebar(Files));
