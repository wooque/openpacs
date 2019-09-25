import React, { useState, useEffect } from 'react';
import { Upload, Button, Icon, Modal, Row, Col } from 'antd';
import { API_URL } from '../config';
import './AdminFiles.css';

export function AdminFiles(props) {
  let [fileList, setFileList] = useState([]);

  const onChange = (info) => {
    let fileList = [...info.fileList];
    fileList = fileList.map(file => {
      if (file.response) {
        file.url = file.response.url;
      }
      return file;
    });
    if (info.file.status === 'done') {
      fileList = fileList.filter(f => f.name !== info.file.name);
    }
    setFileList(fileList);
  };

  useEffect(() => {
    setFileList([]);
  }, [props]);

  return (
    <Modal
      visible={props.visible}
      title="Upload"
      okText="Upload"
      onCancel={props.onClose}
      onOk={props.onClose}
    >
      <Row>
        <Col span={8} >
          <Upload
            name="file"
            multiple={true}
            action={API_URL + '/files/upload'}
            headers={{
              'X-Auth-Pacs': localStorage.getItem('token'),
            }}
            onChange={onChange}
            fileList={fileList}
          >
            <Button>
              <Icon type="upload" /> Upload files
            </Button>
          </Upload>
        </Col>
        <Col span={8} id='upload_directory' >
          <Upload
            action={API_URL + '/files/upload'}
            headers={{
              'X-Auth-Pacs': localStorage.getItem('token'),
            }}
            onChange={onChange}
            fileList={fileList}
            directory
          >
            <Button>
              <Icon type="upload" /> Upload directory
            </Button>
          </Upload>
        </Col>
      </Row>
    </Modal>
  );
}