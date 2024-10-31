
import OrderedCollectionViewer from 'components/OrderedCollectionViewer.js';
import Note from 'components/notes/Note.js';

const InboxViewer = () => {

    const render = (item) => {
        if (item.type === 'Create') {
            return <Note note={item.object} key={item.id} />
        }
    }


    return (
        <>
            <h1>Inbox</h1>
            <OrderedCollectionViewer id="/api/v1/inbox" render={render} />
        </>
    )

}

export default InboxViewer;