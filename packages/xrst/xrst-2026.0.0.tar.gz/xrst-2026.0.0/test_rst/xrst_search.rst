.. _xrst_search-name:

!!!!!!
search
!!!!!!

.. _xrst_search-title:

xrst Keyword Search
*******************

.. raw:: html

   <noscript><h1>
   This search utility requires Javascript to be enabled
   and Javascript is disabled in your browser.
   </h1></noscript>
   <form name='search'>
   <p><table>
      Keywords include the page name, and words in the title or headings.
      Enter Keywords separated by spaces to reduce the match count:
      <tr><td>
         Keywords
      </td><td>
         Match
      </td><tr><td>
         <input
            type='text'
            name='keywords'
            onkeydown='update_match()'
            size='50'
         ></input>
      </td><td>
         <input
            type='text'
            name='match'
            size=5
         ></input>
      </td></tr>
   </table></p>
   <p><table>
      Selecting a page name or ttle below will go to that page:
      <tr><td>
         Page Name
      </td><td>
         Page Title
      </td></tr>
      <tr><td>
         <textarea
            name='name_match'
            rows='20'
            cols='15'
            onclick='select_match(this)'
            ondblclick='goto_match(this)'
            onkeydown='page_or_title_entry(this)'
         ></textarea>
      </td><td>
         <textarea
            name='title_match'
            rows='20'
            cols='50'
            onclick='select_match(this)'
            ondblclick='goto_match(this)'
            onkeydown='page_or_title_entry(this)'
         ></textarea>
      </td></tr>
   </table></p>
   </form>
   <script type='text/javascript' src='xrst_search.js'>
   </script>
