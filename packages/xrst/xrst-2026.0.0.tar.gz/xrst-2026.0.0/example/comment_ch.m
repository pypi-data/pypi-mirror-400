% SPDX-License-Identifier: GPL-3.0-or-later
% SPDX-FileCopyrightText: Bradley M. Bell <bradbell@seanet.com>
% SPDX-FileContributor: 2020-23 Bradley M. Bell
% ----------------------------------------------------------------------------
%
   % {xrst_begin comment_ch_example}
   % {xrst_spell
   %     fac
   % }
   % {xrst_comment_ch %}
   %
   % Comment Character Command Example
   % #################################
   %
   % Discussion
   % **********
   % The comment character at the beginning of a line,
   % and one space, if a space exists directly after it the comment character,
   % are removed before processing xrst commands.
   % For this example, the comment character is ``%`` .
   %
   % xrst_code
   % *********
   % The xrst_code command reports the original source code, before removing
   % the comment character or the indentation.
   % {xrst_code m}
   %
   % set n_fac = n !
   function n_fac = factorial(n)
      if( n == 0 )
         n_fac = 1;
      else
         n_fac =  n * factorial(n-1);
      end
   % {xrst_code}
   %
   % Indent
   % ******
   % Note that the special character ``%`` has the same indentation as
   % the source code in this page.
   %
   % xrst_comment_ch
   % ***************
   % The file below demonstrates the use of ``xrst_comment_ch`` .
   %
   % This Example File
   % *****************
   % {xrst_literal}
   %
   % {xrst_end comment_ch_example}
