import React, { useState } from 'react';
import { withRouter } from 'react-router-dom';
import { Button, message, Layout } from 'antd';
import { request } from '../helpers';
const { Content } = Layout;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function Managment(props) {
  document.title = 'Managment';
  let [loading, setLoading] = useState(false);

  const deleteFile = () => {
    setLoading(true);
    request(`files/${props.file.id}`, { method: 'DELETE' })
      .then(() => sleep(1000))
      .then(() => props.history.push('/'))
      .catch(
        () => message.error('Deletion failed')
      );
  };

  return (
    <Content style={{ padding: 24, background: '#fff', minHeight: 360, maxWidth: 600 }}>
      <Button size="large" type="danger" onClick={deleteFile} disabled={loading}>
        {loading ? 'Deleting...' : 'Delete'}
      </Button>
    </Content>
  );
}

export default withRouter(Managment);
