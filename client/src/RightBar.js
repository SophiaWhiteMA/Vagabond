import {useState} from 'react';
import { ReactComponent as Users } from 'icon/users.svg'
import { ReactComponent as SignIn } from 'icon/sign-in.svg'
import { ReactComponent as SignOut } from 'icon/sign-out.svg'
import { ReactComponent as Bell } from 'icon/bell.svg'
import { ReactComponent as Inbox } from 'icon/inbox.svg';
import { ReactComponent as Feather } from 'icon/feather.svg';
import { ReactComponent as Send } from 'icon/send.svg';
import { ReactComponent as UserPlus } from 'icon/user-plus.svg';
import { ReactComponent as Logo } from 'img/Vagabond_Logo.svg';

const RightBar = (props) => {

    const [visible, setVisible] = useState(true);

    const styleBarInvisible = {
      justifyContent: 'flex-end',
      background: '#454545',
      marginTop: '30px'
    };

    const styleButtonInvisible = {
      fontSize: '18px',
      background: 'white'
    };

    const toggleVisibility = () => {
      setVisible(!visible);
    }

    return (
      <div id="sidebar-right">
        <div id="hideBarRight" style={visible ? {} : styleBarInvisible} className="sidebar-top-bar">
          <button id="hideButtonRight" style={visible ? {} : styleButtonInvisible} className="visibility-button" onClick={toggleVisibility} >
            {visible ? "-" : "About"}
          </button>
        </div>
        {
          visible &&
          <div id="rightBar" className="bar" style={{display:'flex',flexDirection:'column',justifyContent:'flex-start',overflowY:'scroll'}}>
            <h1 className="dark" style={{paddingTop:'0'}}>About Vagabond</h1>
            <br />
            <p style={{fontSize:'15px',margin:'0 25px 0 25px'}}>
            Vagabond is a distributed, privacy-respecting social network built using the ActivityPub protocol. Vagabond is free and open source (GPLv3), and no single entity owns or controls it, giving control and peace of mind back to the end user.
            Whether you're a casual user or a tech enthusist looking to create your own instance, using Vagabond is easy.
            </p>
            <br/>
            <h1 className="dark" style={{paddingTop:'0'}}>Help</h1>
            <br />
            <div style={{display:'flex',flexDirection:'row',margin:'0 25px 0 25px'}}>
              <SignIn/>
              <p style={{fontSize:'15px',margin:'0 10px 0 10px'}}>Sign in, register or sign out of your account.</p>
            </div>
            <br />
            <div style={{display:'flex',flexDirection:'row',margin:'0 25px 0 25px'}}>
              <UserPlus/>
              <p style={{fontSize:'15px',margin:'0 10px 0 10px'}}>Follow an account with the complete handle.</p>
            </div>
            <br />
            <div style={{display:'flex',flexDirection:'row',margin:'0 25px 0 25px'}}>
              <Inbox/>
              <p style={{fontSize:'15px',margin:'0 10px 0 10px'}}>Notes from the accounts you follow.</p>
            </div>
            <br />
            <div style={{display:'flex',flexDirection:'row',margin:'0 25px 0 25px'}}>
              <Send/>
              <p style={{fontSize:'15px',margin:'0 10px 0 10px'}}>Notes posted by you.</p>
            </div>
            <br />
            <div style={{display:'flex',flexDirection:'row',margin:'0 25px 0 25px'}}>
              <Bell/>
              <p style={{fontSize:'15px',margin:'0 10px 0 10px'}}>Notifications (follows, likes, mentions).</p>
            </div>
            <br />
            <div style={{display:'flex',flexDirection:'row',margin:'0 25px 0 25px'}}>
              <Feather/>
              <p style={{fontSize:'15px',margin:'0 10px 0 10px'}}>Create a note.</p>
            </div>
          </div>
        }
      </div>
    );
  }

  export default RightBar;