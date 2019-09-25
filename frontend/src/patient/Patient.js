import React, { useState, useEffect } from 'react';
import { Layout, message, Tree, Table } from 'antd';
import withSidebar from '../common/base';
import { request } from '../helpers';
import { withRouter } from 'react-router-dom';

const Content = Layout.Content;
const { TreeNode, DirectoryTree } = Tree;

const columns = [
  {
    dataIndex: 'key',
    width: '20%',
  },
  {
    dataIndex: 'value',
  },
];

const mappings = [
  {
    key: 'patient_id',
    title: 'Patient ID',
  },
  {
    key: 'name',
    title: 'Patient Name'
  },
  {
    key: 'sex',
    title: 'Patient Sex'
  },
  {
    key: 'birth_date',
    title: 'Patient Birth Date'
  },
];

function wrap(txt) {
  if (!txt) return '';
  return `(${txt})`;
}

function Patient(props) {
  document.title = 'Patient';

  let [data, setData] = useState({});
  let [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    let params = props.match.params;
    request(`patients/${params.id}`).then(data => {
      setLoading(false);
      setData(data);

    }).catch(e => {
      setLoading(false);
      message.error(e.message);
    });
    // eslint-disable-next-line
  }, []);

  const onSelect = s => {
    props.history.push(`/files/${s}`);
  };

  const data2 = [];
  for (let m of mappings) {
    data2.push({ key: m.title, value: data[m.key] });
  }
  return (
    <Content style={{
      alignItems: 'center',
      justifyContent: 'center',
      padding: '50px 10px 10px 10px'
    }}>
      <Table
        style={{ marginBottom: '10px' }}
        scroll={{ x: 500 }}
        columns={columns}
        rowKey={record => record.key}
        dataSource={data2}
        loading={loading}
        pagination={{ position: 'none' }}
        showHeader={false}
      />
      <p style={{ marginBottom: '0px' }}>Studies</p>
      <DirectoryTree defaultExpandAll onSelect={onSelect}>
        {
          data && data.studies && data.studies.map(s => {
            return (
              <TreeNode
                title={`Study ${s.study_id} ${wrap(s.description)}`}
                key={s.id}
                selectable={false}
              >
                {
                  s.series && s.series.map(sr => {
                    return (
                      <TreeNode
                        title={`Series ${sr.number} ${wrap(sr.description)}`}
                        key={sr.id}
                        selectable={false}
                      >
                        {
                          sr.files && sr.files.map(f => {
                            return (
                              <TreeNode
                                title={`File ${f.name}`}
                                key={f.id}
                                isLeaf
                              />
                            );
                          })
                        }
                      </TreeNode>
                    );
                  })
                }
              </TreeNode>
            );
          })}
      </DirectoryTree>
    </Content>
  );
}

export default withRouter(withSidebar(Patient));
