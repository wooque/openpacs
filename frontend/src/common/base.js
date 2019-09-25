import React from 'react';
import Sidebar from './Sidebar';
import { Layout } from 'antd';

function withSidebar(Comp) {
  function wrapper(props) {
    const tempKey = localStorage.getItem('tempKey');
    return (
      <Layout style={{
        minHeight: '100vh',
      }}>
        {!tempKey && <Sidebar {...props} />}
        <Comp {...props} />
      </Layout>
    );
  }
  return wrapper;
}

export default withSidebar;