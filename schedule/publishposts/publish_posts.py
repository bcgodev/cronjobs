from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import argparse
import logging
import os
import yaml


logging.basicConfig()


def main(config_graphql: dict = None):
    ''' Import YouTube Channel program starts here '''
    logger = logging.getLogger(__file__)
    logger.setLevel('INFO')

    cms_graphql_endpoint = config_graphql['apiEndpoint']
    gql_transport = RequestsHTTPTransport(
        url=cms_graphql_endpoint,
        use_json=True,
        headers={
            "Content-type": "application/json",
        },
        verify=True,
        retries=3,
    )

    gql_client = Client(
        transport=gql_transport,
        fetch_schema_from_transport=False,
    )

    # Authenticate through GraphQL
    qgl_mutation_authenticate_get_token = '''
    mutation {
    authenticate: authenticateUserWithPassword(email: "%s", password: "%s") {
        token
    }
    }
    '''

    username = config_graphql['username']
    password = config_graphql['password']

    mutation = gql(qgl_mutation_authenticate_get_token % (username, password))

    token = gql_client.execute(mutation)['authenticate']['token']

    print(f'{os.path.basename(__file__)} has authenticated as {username}')

    gql_transport_with_token = RequestsHTTPTransport(
        url=cms_graphql_endpoint,
        use_json=True,
        headers={
            "Content-type": "application/json",
            'Authorization': f'Bearer {token}'
        },
        verify=True,
        retries=3,
    )

    gql_authenticated_client = Client(
        transport=gql_transport_with_token,
        fetch_schema_from_transport=False,
    )

    now = datetime.utcnow().isoformat(timespec='microseconds') + "Z"

    query_scheduled_posts = '''
    {
        allPosts(where: {state: scheduled, publishTime_lte: "%s"}) {
            id
        }
    }
    ''' % now

    all_posts = gql_authenticated_client.execute(
        gql(query_scheduled_posts))['allPosts']

    data = ['{id: %s, data:{state: published, publishTime: "%s"}}' % (post['id'], now)
            for post in all_posts]

    if len(data) != 0:
        publish_mutation = '''
        mutation {
            updatePosts(data: [%s]){
                id
                name
                state
            }
        }
        ''' % ' ,'.join(data)

        updatePosts = gql_authenticated_client.execute(
            gql(publish_mutation))['updatePosts']
        for post in updatePosts:
            logger.info(
                f'post(id: {post["id"]}) {post["name"]} is {post["state"]}')
    else:
        logger.info('there is no scheduled post ready to be published')


__GRAPHQL_CMS_CONFIG_KEY = 'graphqlCMS'

if __name__ == '__main__':
    logger = logging.getLogger(__file__)
    logger.setLevel('INFO')
    logger.info(f'{__file__} is executing...')
    parser = argparse.ArgumentParser(
        description=f'Process configuration of {__file__}')
    parser.add_argument('-g', '--config-graphql', dest=__GRAPHQL_CMS_CONFIG_KEY,
                        help=f'graphql config file for {__file__} ', metavar='FILE', type=str, required=True)

    args = parser.parse_args()

    with open(getattr(args, __GRAPHQL_CMS_CONFIG_KEY), 'r') as stream:
        config_graphql = yaml.safe_load(stream)

    main(config_graphql=config_graphql)

    logger.info('exiting...good bye...')