/**
 *
 * RewardingModal
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
import { compose } from 'redux';

import LoadingDots from 'components/LoadingDots';
import { withModal } from 'components/withModal';

import { graphql } from 'react-apollo';

import RewardingModalQuery from 'graphql/RewardingModalQuery';
import RewardingModalComponent from './RewardingModalComponent';

export function RewardingModal(props) {
  const { loading, error, puzzle } = props;
  if (error) {
    return <div>{error.message}</div>;
  } else if (loading) {
    return <LoadingDots />;
  }
  return (
    <RewardingModalComponent
      title={props.title}
      genre={props.genre}
      yami={props.yami}
      id={props.id}
      {...puzzle}
    />
  );
}

RewardingModal.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  genre: PropTypes.number.isRequired,
  yami: PropTypes.bool.isRequired,
  puzzle: PropTypes.object,
  loading: PropTypes.bool.isRequired,
  error: PropTypes.shape({
    message: PropTypes.string.isRequired,
  }),
};

const withData = graphql(RewardingModalQuery, {
  options: ({ id }) => ({
    variables: {
      id,
    },
  }),
  props({ data }) {
    const { puzzle, loading, error } = data;
    return {
      puzzle,
      loading,
      error,
    };
  },
});

export default compose(withModal({}), withData)(RewardingModal);
