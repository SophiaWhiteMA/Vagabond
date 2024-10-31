import { ReactComponent as NotFound } from 'icon/404.svg';

const Error404 = () => {

    return (
        <div style={{display:'flex',flexDirection:'column'}}>
            <h1 style={{fontSize:'30px',fontWeight:'bolder', textAlign:'center',margin:'30px 0 30px 0'}}>Error 404: Page Not Found</h1>
            <NotFound style={{width:'80%',marginRight:'auto',marginLeft:'auto'}}/>
        </div>
    );

}

export default Error404;