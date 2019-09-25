import React from 'react';
import { withRouter } from 'react-router-dom';
import { parseParams, encodeQuery } from '../helpers';

function LinkExt(props) {
  let {history, reload} = props;
  let {pathname, search} = history.location;
  let loc = pathname + search;
  let href;

  if (props.to) {
    href = props.to;

  } else if (props.query) {
    if (loc.includes('?')) {
      let params = parseParams(search);
      params = Object.assign(params, props.query);
      href = pathname + '?' + encodeQuery(params);
    } else {
      href = loc + '?' + encodeQuery(props.query);
    }
  }

  const navigate = (event) => {
    event.preventDefault();

    if (loc !== href) {
      history.push(href);
    } else {
      if (reload) reload();
    }
  };
  
  return (
    <a href={href} onClick={navigate}>{props.children}</a>
  );
}

export default withRouter(LinkExt);
