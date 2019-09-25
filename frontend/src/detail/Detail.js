import React, { useState, useEffect } from 'react';
import { Link, withRouter } from 'react-router-dom';
import { Layout, message, Icon, Menu, Breadcrumb } from 'antd';
import withSidebar from '../common/base';
import { request, isAdmin } from '../helpers';
import { API_URL } from '../config';
import CornerstoneElement from './CornerstoneElement';
import EditableTable from './EditableTable';
import Changes from './Changes';
import Share from './Share';
import Managment from './Managment';
import './Detail.css';

const Content = Layout.Content;

function wrap(txt) {
  if (!txt) return '';
  return `(${txt})`;
}

function Detail(props) {
  document.title = 'Detail';
  const imagePath = `wadouri:${API_URL}/files/${props.match.params.id}/data`;

  let [tab, setTab] = useState('image');
  let [data, setData] = useState({});
  let [loading, setLoading] = useState(false);
  let [key, setKey] = useState(1);
  let [study, setStudy] = useState(null);
  let [series, setSeries] = useState(null);
  let [image, setImage] = useState(imagePath);

  useEffect(() => {
    setLoading(true);
    let params = props.match.params;

    setImage(`wadouri:${API_URL}/files/${params.id}/data`);

    request(`files/${params.id}`).then(data => {
      setLoading(false);
      for (let s of data.patient.studies) {
        if (s.id === data.study_db_id) {
          setStudy(s);
          for (let sr of s.series) {
            if (sr.id === data.series_db_id) {
              setSeries(sr);
            }
          }
        }
      }
      setData(data);

      // hack to trigger re-render, to help cornerstone initialization
      if (!window.ctinit) {
        window.ctinit = true;
        setTimeout(() => {
          setKey(2);
        }, 500);
      }

    }).catch(e => {
      setLoading(false);
      let msg = 'File fail to load';
      if (e.message === '404') {
        msg = 'File not found';
      }
      message.error(msg);
      if (e.message === '404') {
        props.history.push('/');
      }
    });
    // eslint-disable-next-line
  }, [props.match.params.id]);

  const background = tab === 'image' ? '#000' : '';

  const changeStudy = (e, s) => {
    e.preventDefault();
    setStudy(s);
    setSeries(s.series[0]);
  };

  const studiesDrop = data => {
    if (!data) return null;
    return (
      <Menu>
        {
          data.map(d => {
            return (
              <Menu.Item key={d.study_id}>
                {/* eslint-disable-next-line */}
                <a href="" onClick={e => changeStudy(e, d)}>
                  {`Study ${d.study_id} ${wrap(d.description)}`}
                </a>
              </Menu.Item>
            );
          })
        }
      </Menu>
    );
  };

  const changeSeries = (e, s) => {
    e.preventDefault();
    setSeries(s);
  };

  const seriesDrop = data => {
    if (!data) return null;
    return (
      <Menu>
        {
          data.map(d => {
            return (
              <Menu.Item key={d.number}>
                {/* eslint-disable-next-line */}
                <a href='' onClick={e => changeSeries(e, d)}>
                  {`Series ${d.number} ${wrap(d.description)}`}
                </a>
              </Menu.Item>
            );
          })
        }
      </Menu>
    );
  };

  const filesDrop = data => {
    if (!data) return null;
    return (
      <Menu>
        {
          data.map(d => {
            return (
              <Menu.Item key={d.id}>
                <Link to={`/files/${d.id}`}>
                  {`File ${d.name}`}
                </Link>
              </Menu.Item>
            );
          })
        }
      </Menu>
    );
  };

  const tempKey = localStorage.getItem('tempKey');

  return (
    <Content style={{
      alignItems: 'center',
      justifyContent: 'center',
      background: background,
    }}>
      <Menu style={{ paddingLeft: '40px' }} defaultSelectedKeys={[tab]} mode="horizontal">
        <Menu.Item key="image" onClick={() => setTab('image')} >
          <Icon type="eye" />
          Image
        </Menu.Item>
        <Menu.Item key="data" onClick={() => setTab('data')} >
          <Icon type="table" />
          Data
        </Menu.Item>
        {
          !tempKey &&
          <Menu.Item key="share" onClick={() => setTab('share')} >
            <Icon type="share-alt" />
            Share
          </Menu.Item>
        }
        {
          !tempKey &&
          <Menu.Item key="changes" onClick={() => setTab('changes')} >
            <Icon type="history" />
            Changes
          </Menu.Item>
        }
        {
          !tempKey && isAdmin() &&
          <Menu.Item key="admin" onClick={() => setTab('admin')} >
            <Icon type="lock" />
            Admin
          </Menu.Item>
        }
      </Menu>
      {
        data && data.patient && ['image'].includes(tab) &&
        <Breadcrumb style={{ background: '#fff', padding: '5px' }}>
          <Breadcrumb.Item>
            <Link to={`/patients/${data.patient_id}`}>
              {`${data.patient.name} (${data.patient.patient_id})`}
            </Link>
          </Breadcrumb.Item>
          <Breadcrumb.Item overlay={studiesDrop(data.patient.studies)}>
            {`Study ${study.study_id} ${wrap(study.description)}`}
          </Breadcrumb.Item>
          <Breadcrumb.Item overlay={seriesDrop(study.series)}>
            {`Series ${series.number} ${wrap(series.description)}`}
          </Breadcrumb.Item>
          <Breadcrumb.Item overlay={filesDrop(series.files)}>
            {`File ${data.name}`}
          </Breadcrumb.Item>
        </Breadcrumb>
      }
      <CornerstoneElement key={key}
        file={data}
        files={series? series.files: null}
        changeFile={v => props.history.push(`/files/${series.files[v].id}`)}
        image={image}
        visible={tab === 'image'}
      />
      <EditableTable
        style={tab !== 'data' ? { display: 'none' } : {}}
        rowKey={record => record.key}
        pagination={{ pageSize: 20 }}
        file={data}
        loading={loading}
      />
      {tab === 'changes' && <Changes file={data}></Changes>}
      {tab === 'share' && <Share file={data}></Share>}
      {tab === 'admin' && isAdmin() && <Managment file={data}></Managment>}
    </Content>
  );
}

export default withSidebar(withRouter(Detail));
